from library.storage import PostgreSQL
from .group import admin_group
import lightbulb
import hikari

@admin_group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    name="allowed",
    name_localizations={
        "en-GB": "allowed",
        "es-ES": "permitido",
        "fr": "autorisé"
    },
    description="Whether to allow multiple jobs.",
    description_localizations={
        "en-GB": "Whether to allow multiple jobs.",
        "es-ES": "Si se permiten múltiples trabajos.",
        "fr": "Autoriser plusieurs emplois."
    },
    type=hikari.OptionType.BOOLEAN,
    required=True
)
@lightbulb.add_cooldown(bucket=lightbulb.buckets.GuildBucket, length=5, uses=1)
@lightbulb.add_checks(
    lightbulb.has_guild_permissions(hikari.Permissions.ADMINISTRATOR)
)
@lightbulb.command(
    name="multijob",
    name_localizations={
        "en-GB": "multijob",
        "es-ES": "multitrabajo",
        "fr": "multitravail"
    },
    description="Set whether to allow multiple jobs.",
    description_localizations={
        "en-GB": "Set whether to allow multiple jobs.",
        "es-ES": "Establece si se permiten múltiples trabajos.",
        "fr": "Définir si autoriser plusieurs emplois."
    },
    pass_options=True
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def command(ctx: lightbulb.SlashContext, allowed:bool) -> None:
    guild_pg = PostgreSQL.guild(ctx.guild_id)
    localize = guild_pg.localize
    success = guild_pg.set_multijob_rule(allowed)

    if success is True:
        embed = (
            hikari.Embed(
                title=localize('Success!'),
                description=localize("The multijob rule has been set to %s.", variables=(localize(str(allowed)),)),
                color=0x00FF00  # Green color
            )
        )
    else:
        embed = (
            hikari.Embed(
                title=localize('Error!'),
                description=localize("The multijob rule could not be set to %s.", variables=(localize(str(allowed)),)),
                color=0xFF0000  # Red color
            )
        )

    await ctx.respond(embed)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
