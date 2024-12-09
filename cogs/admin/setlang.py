from library.storage import PostgreSQL
from .group import admin_group
import lightbulb
import hikari

@admin_group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    name="language",
    name_localizations={
        "en-GB": "language",
        "es-ES": "idioma",
        "fr": "langue"
    },
    description="The language to set the bot to.",
    description_localizations={
        "en-GB": "The language to set the bot to.",
        "es-ES": "El idioma al que establecer el bot.",
        "fr": "La langue à définir pour le bot."
    },
    choices=[
        "English",
        "Español",
        "Français"
    ],
    type=hikari.OptionType.STRING,
    required=True
)
@lightbulb.add_cooldown(bucket=lightbulb.buckets.GuildBucket, length=5, uses=1)
@lightbulb.command(
    name="setlang",
    name_localizations={
        "en-GB": "setlang",
        "es-ES": "estableceridioma",
        "fr": "définirlangue"
    },
    description="Set the language of the bot for the guild.",
    description_localizations={
        "en-GB": "Set the language of the bot for the guild.",
        "es-ES": "Establezca el idioma del bot para el gremio.",
        "fr": "Définissez la langue du bot pour la guilde."
    },
    pass_options=True
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def command(ctx: lightbulb.SlashContext, language) -> None:
    lang_map = {
        "English": "en",
        "Español": "es",
        "Français": "fr"
    }

    PostgreSQL.guild(ctx.guild_id).set_language(
        language=lang_map[language]
    )
    localize = PostgreSQL.guild(ctx.guild_id).localize

    embed = (
        hikari.Embed(
            title=localize('Language set successfully!'),
            description=localize("Understand me better now?"),
            color=0x00FF00  # Green color
        )
    )

    await ctx.respond(embed)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
