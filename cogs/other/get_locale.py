from library.storage import PostgreSQL
from library.botapp import botapp
import lightbulb

@botapp.command
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.add_cooldown(bucket=lightbulb.buckets.GuildBucket, length=5, uses=1)
@lightbulb.command(
    name="getlocale",
    name_localizations={
        "en-GB": "getlocale",
        "es-ES": "obtenerlocal",
        "fr": "obtenirlocale"
    },
    description="Get the locale of the guild.",
    description_localizations={
        "en-GB": "Get the locale of the guild.",
        "es-ES": "Obtener la configuración regional del servidor.",
        "fr": "Obtenir la configuration régionale de la guilde"
    },
)
@lightbulb.implements(lightbulb.SlashCommand)
async def command(ctx: lightbulb.SlashContext) -> None:
    localize = PostgreSQL.guild(ctx.guild_id).localize
    locale = ctx.get_guild().preferred_locale
    await ctx.respond(f"{localize("Locale")}: {locale}")

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
