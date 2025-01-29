from library.storage import PostgreSQL
from .group import market_group
import lightbulb
import hikari

@market_group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    name="value",
    name_localizations={
        "en-GB": "value",
        "es-ES": "valor",
        "fr": "valeur"
    },
    description="The value of the item.",
    description_localizations={
        "en-GB": "The value of the item.",
        "es-ES": "El valor del artículo.",
        "fr": "La valeur de l'article."
    },
    type=hikari.OptionType.INTEGER,
    required=True
)
@lightbulb.option(
    name="description",
    name_localizations={
        "en-GB": "description",
        "es-ES": "descripción",
        "fr": "description"
    },
    description="The description of the item.",
    description_localizations={
        "en-GB": "The description of the item.",
        "es-ES": "La descripción del artículo.",
        "fr": "La description de l'article."
    },
    type=hikari.OptionType.STRING,
    required=True
)
@lightbulb.option(
    name="name",
    name_localizations={
        "en-GB": "name",
        "es-ES": "nombre",
        "fr": "nom"
    },
    description="The name of the item.",
    description_localizations={
        "en-GB": "The name of the item.",
        "es-ES": "El nombre del artículo.",
        "fr": "Le nom de l'article."
    },
    type=hikari.OptionType.STRING,
    required=True
)
@lightbulb.option(
    name="rarity",
    name_localizations={
        "en-GB": "rarity",
        "es-ES": "rareza",
        "fr": "rareté"
    },
    description="The rarity of the item.",
    description_localizations={
        "en-GB": "The rarity of the item.",
        "es-ES": "La rareza del artículo.",
        "fr": "La rareté de l'article."
    },
    type=hikari.OptionType.STRING,
    required=False,
    choices=['common', 'uncommon', 'rare', 'epic', 'legendary'],
    default='common'
)
@lightbulb.option(
    name='tradable',
    name_localizations={
        "en-GB": "tradable",
        "es-ES": "comerciable",
        "fr": "échangeable"
    },
    description="Whether the item is tradable.",
    description_localizations={
        "en-GB": "Whether the item is tradable.",
        "es-ES": "Si el artículo es comerciable.",
        "fr": "Si l'article est échangeable."
    },
    type=hikari.OptionType.BOOLEAN,
    required=False,
    default=True
)
@lightbulb.add_cooldown(bucket=lightbulb.buckets.UserBucket, length=3, uses=1)
@lightbulb.command(
    name="add",
    name_localizations={
        "en-GB": "add",
        "es-ES": "añadir",
        "fr": "ajouter"
    },
    description="Add an item to the market.",
    description_localizations={
        "en-GB": "Add an item to the market.",
        "es-ES": "Agregue un artículo al mercado.",
        "fr": "Ajouter un article au marché."
    },
    pass_options=True
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def command(ctx: lightbulb.SlashContext, name:str, description:str, value:int, rarity:str, tradable:bool) -> None:
    guild_pg = PostgreSQL.guild(ctx.guild_id)
    localize = guild_pg.localize

    rarity_crossref = {
        'common': 1,
        'uncommon': 2,
        'rare': 3,
        'epic': 4,
        'legendary': 5
    }

    if rarity not in rarity_crossref:
        embed = (
            hikari.Embed(
                title=localize("Invalid rarity."),
                description=localize("The rarity must be one of common, uncommon, rare, epic, or legendary."),
                colour=0xFF0000
            )
            .set_author(name=ctx.author.username, icon=ctx.author.avatar_url)
        )
        await ctx.respond(embed=embed)
        return

    success = guild_pg.market.add_item(
        name=name,
        description=description,
        value=value,
        rarity=rarity_crossref[rarity],
        tradable=tradable
    )

    if success:
        embed = (
            hikari.Embed(
                title=localize("Item added to the market."),
                description=localize("The item has been added to the market."),
                colour=0x00FF00
            )
            .set_author(name=ctx.author.username, icon=ctx.author.avatar_url)
        )
    else:
        embed = (
            hikari.Embed(
                title=localize("Item not added to the market."),
                description=localize("The item could not be added to the market."),
                colour=0xFF0000
            )
            .set_author(name=ctx.author.username, icon=ctx.author.avatar_url)
        )

    await ctx.respond(embed=embed)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
