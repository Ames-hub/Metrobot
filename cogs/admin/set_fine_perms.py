import psycopg2.errors

from library.storage import PostgreSQL
from .group import admin_group
import lightbulb
import hikari

@admin_group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    name="role",
    name_localizations={
        "en-GB": "role",
        "es-ES": "rol",
        "fr": "rôle"
    },
    description="Which role to give the permission to.",
    description_localizations={
        "en-GB": "Which role to give the permission to.",
        "es-ES": "A qué rol dar el permiso.",
        "fr": "Quel rôle donner la permission à."
    },
    type=hikari.OptionType.USER,
    required=True
)
@lightbulb.add_cooldown(bucket=lightbulb.buckets.UserBucket, length=5, uses=1)
@lightbulb.add_checks(
    lightbulb.has_guild_permissions(hikari.Permissions.ADMINISTRATOR)
)
@lightbulb.command(
    name="set_fine_perms",
    name_localizations={
        "en-GB": "set_fine_perms",
        "es-ES": "dar_permisos_multa",
        "fr": "donner_permissions_amende"
    },
    description="Give a role the ability to fine other users.",
    description_localizations={
        "en-GB": "Give a role the ability to fine other users.",
        "es-ES": "Dar a un rol la capacidad de multar a otros usuarios.",
        "fr": "Donner à un rôle la capacité d'amender d'autres utilisateurs."
    },
    pass_options=True
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def command(ctx: lightbulb.SlashContext, role: hikari.Role) -> None:
    localize = PostgreSQL.guild(ctx.guild_id).localize

    try:
        PostgreSQL.guild(ctx.guild_id).set_fine_perms_as(role.id)
    except psycopg2.errors.UniqueViolation:
        await ctx.respond(localize("Uh oh, something went wrong!") + " :(")
        return

    await ctx.respond(localize("Fine permissions have been set!"))


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
