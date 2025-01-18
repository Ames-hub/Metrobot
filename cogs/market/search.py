from library.storage import PostgreSQL
from .group import market_group
import lightbulb
import hikari

@market_group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    name="page_numb",
    name_localizations={
        "en-GB": "page",
        "es-ES": "página",
        "fr": "page"
    },
    description="What page of the market to view.",
    description_localizations={
        "en-GB": "What page of the market to view.",
        "es-ES": "Qué página del mercado ver.",
        "fr": "Quelle page du marché voir."
    },
    type=hikari.OptionType.INTEGER,
    default=1,
    min_value=1,
    required=False
)
@lightbulb.add_cooldown(bucket=lightbulb.buckets.UserBucket, length=3, uses=1)
@lightbulb.command(
    name="view",
    name_localizations={
        "en-GB": "view",
        "es-ES": "ver",
        "fr": "voir"
    },
    description="View the market and what is available.",
    description_localizations={
        "en-GB": "View the market and what is available.",
        "es-ES": "Ver el mercado y lo que está disponible.",
        "fr": "Voir le marché et ce qui est disponible."
    },
    pass_options=True
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def command(ctx: lightbulb.SlashContext, page_numb:int) -> None:
    guild_pg = PostgreSQL.guild(ctx.guild_id)
    localize = guild_pg.localize

    # Each page is a division of 25 items.
    guild_pg.market

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
