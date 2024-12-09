from library.storage import PostgreSQL
from .group import admin_group
import lightbulb
import hikari

@admin_group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    name="payday",
    name_localizations={
        "en-GB": "payday",
        "es-ES": "pago",
        "fr": "paie"
    },
    description="The day of the week to pay the users. To make it Monday, set it to 1.",
    description_localizations={
        "en-GB": "The day of the week to pay the users. To make it Monday, set it to 1.",
        "es-ES": "El día de la semana para pagar a los usuarios. Para hacerlo el lunes, ponlo en 1.",
        "fr": "Le jour de la semaine pour payer les utilisateurs. Pour le lundi, mettez-le à 1."
    },
    min_value=1,
    max_value=7,
    type=hikari.OptionType.INTEGER,
    required=True
)
@lightbulb.add_cooldown(bucket=lightbulb.buckets.GuildBucket, length=5, uses=1)
@lightbulb.add_checks(
    lightbulb.has_guild_permissions(hikari.Permissions.ADMINISTRATOR)
)
@lightbulb.command(
    name="payday",
    name_localizations={
        "en-GB": "payday",
        "es-ES": "pago",
        "fr": "paie"
    },
    description="Set the day of the week to pay the users.",
    description_localizations={
        "en-GB": "Set the day of the week to pay the users.",
        "es-ES": "Establece el día de la semana para pagar a los usuarios.",
        "fr": "Définir le jour de la semaine pour payer les utilisateurs."
    },
    pass_options=True
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def command(ctx: lightbulb.SlashContext, payday:int) -> None:
    weekday_map = {
        1: "Monday",
        2: "Tuesday",
        3: "Wednesday",
        4: "Thursday",
        5: "Friday",
        6: "Saturday",
        7: "Sunday"
    }

    guild_pg = PostgreSQL.guild(ctx.guild_id)
    localize = guild_pg.localize

    payday = localize(weekday_map[payday])
    guild_pg.set_payday(payday)

    await ctx.respond(
        localize(
            f"Payday has been set to %s.",
            variables=(payday,)
        ),
    )

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
