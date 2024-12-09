from library.storage import PostgreSQL
from library.botapp import botapp
import lightbulb
import hikari

class bot_plugin(lightbulb.Plugin):
    @staticmethod
    @botapp.listen(hikari.GuildJoinEvent)
    async def listener(event: hikari.GuildJoinEvent) -> None:
        guild = event.get_guild()
        sys_channel_id = guild.system_channel_id

        if sys_channel_id is None:
            return  # No system channel to send the message to

        locale = guild.preferred_locale[:2].lower()
        language_known = True
        if locale not in ['en', 'es', 'fr']:
            # Language not supported, default to English.
            locale = 'en'
            language_known = False

        PostgreSQL.guild(event.guild_id).set_language(
            language=locale
        )
        localize = PostgreSQL.guild(event.guild_id).localize

        if language_known:
            embed = (
                hikari.Embed(
                    title=localize('Thank you for picking me!'),
                    description=localize("To get started, please set your server's language if this is not already accurate!"),
                    color=0x00FF00  # Green color
                )
                .add_field(
                    name=localize("How to set your language"),
                    value=localize("Run `/admin language` to set your server's language.")
                )
                .add_field(
                    name=localize("Set your payday"),
                    value=localize("I am an economy bot, and we use a payday. Run `/admin payday` to set your server's payday! It is NOT set by default.")
                )
            )
        else:
            embed = (
                hikari.Embed(
                    title="🥲",
                    description="🤖💬 ❌ **Your local language is not known by me**\n"
                                "https://translate.google.com/",  # Link for the user to translate the message to their language
                    color=0x0000FF  # blue color
                )
            )

        await botapp.rest.create_message(
            sys_channel_id,
            embed
        )

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
