from library.encryption import encryption
from library.storage import var
from lightbulb.ext import tasks
import lightbulb
import datetime
import logging
import hikari
import os

os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    filename=f'logs/{datetime.datetime.now().strftime("%Y-%m-%d")}.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

keys = encryption('library/private.key')
TOKEN = keys.decrypt(var.get('token'))

botapp = lightbulb.BotApp(
    token=TOKEN,
    intents=hikari.Intents.GUILD_MESSAGE_REACTIONS + hikari.Intents.GUILDS
)
tasks.load(botapp)

botapp.d['permissions_cache'] = {}
botapp.d['colourless'] = hikari.Colour(0x2b2d31)
botapp.d['guild_sys_channels'] = {}

class permissions:
    @staticmethod
    async def check(
            permission,
            member: hikari.Member | hikari.User = None, guild: hikari.Guild = None,  # Method 1
            uuid=str or None, guid=str or None  # Method 2
    ):

        """
        A Permission checker. this will return if the user in the guild is allowed to issue a certain command or not
        according to discord permissions policy. This will return a boolean value. True if the user is allowed, False if not.
        """
        # Prevents circular imports if imported here
        from library.cache import cache
        # Assume for safety
        allowed = False

        if guild is not None:
            guid = guild.id
        if member is not None:
            uuid = member.id
            guid = member.guild_id

        if guid is None:
            raise ValueError("No guild ID was provided. Please provide a guild ID.")

        cached_perms = cache.get_permissions(uuid, guid)
        if cached_perms == -1:
            try:
                checked_member = await botapp.rest.fetch_member(hikari.Snowflake(guid), hikari.Snowflake(uuid))
            except hikari.errors.ForbiddenError:
                return False
            except hikari.errors.NotFoundError:
                return False

            try:
                checked_member = checked_member.get_top_role()
                permissions = checked_member.permissions
                cache.cache_perms(uuid, guid, permissions)
            except Exception as err:
                logging.error(err)
                return False
        else:
            permissions = cached_perms

        if not isinstance(permission, list):
            # If `permission` is not a list, it means it's a single permission.
            # In this case, check if this single permission is in the `permissions`.
            # The result (True or False) is stored in the `allowed` variable.
            allowed = permission in permissions
        else:
            for perm in permission:
                # If `permission` is a list, it means there are multiple permissions to check for.
                # Iterate over each permission in the `permission` list.
                allowed = perm in permissions
                if allowed:
                    break
        # If the member is the owner of the guild, they are allowed to do anything
        try:
            if not allowed:

                allowed = hikari.Permissions.ADMINISTRATOR in permissions

                if allowed is not False:
                    return allowed  # If the member is an admin, return True

                # If the member is the owner of the guild, they are allowed to do anything
                if guid is not None:
                    guild = await botapp.rest.fetch_guild(hikari.Snowflake(guid))
                    if str(guild.owner_id) in str(member.id) or str(guild.owner_id) in str(uuid):
                        allowed = True
        except Exception as err:
            logging.error(err)
            pass

        return allowed