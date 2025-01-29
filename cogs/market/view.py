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

    market_list = guild_pg.market.list_market_items()

    embed = (
        hikari.Embed(
            title=localize("Market | Page %s", variables=(page_numb,)),
            description=localize("Here are the items available for purchase."),
            colour=0x00FF00
        )
        .set_author(name=ctx.author.username, icon=ctx.author.avatar_url)
    )

    items_per_page = 15
    from_item = (page_numb - 1) * items_per_page

    try:
        market_list = market_list[from_item:from_item + items_per_page]
    except KeyError: # Less than 15 items
        if len(market_list) == 0:
            embed.add_field(
                name=localize("Items"),
                value=localize("No items available.")
            )
            await ctx.respond(embed=embed)
            return

    rarity_crossref = {
        1: localize("Common"),
        2: localize("Uncommon"),
        3: localize("Rare"),
        4: localize("Epic"),
        5: localize("Legendary"),
        6: localize("Truly Unique")
    }

    for item in market_list:
        embed.add_field(
            name=f"{market_list[item]['item_name']}",
            value=localize(
                "%s%s | %s | %s tradable<br>%s",
                variables=(
                    localize("$"),
                    market_list[item]['value'],
                    localize(rarity_crossref[market_list[item]['rarity']]),
                    "" if market_list[item]['tradable'] else localize("Not"),
                    market_list[item]['description']
                ),
            ),
            inline=True
        )

    await ctx.respond(embed=embed)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
