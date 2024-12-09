from library.storage import PostgreSQL
from .group import job_group
import lightbulb
import datetime
import hikari

@job_group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.add_cooldown(bucket=lightbulb.buckets.UserBucket, length=30, uses=1)
@lightbulb.command(
    name="payday",
    name_localizations={
        "en-GB": "payday",
        "es-ES": "pago",
        "fr": "paie"
    },
    description="When you get paid.",
    description_localizations={
        "en-GB": "When you get paid.",
        "es-ES": "Cuando te pagan.",
        "fr": "Quand vous êtes payé."
    },
    pass_options=True
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def command(ctx: lightbulb.SlashContext) -> None:
    guild_pg = PostgreSQL.guild(ctx.guild_id)
    localize = guild_pg.localize
    guild_pg.ensure_guild_exists()

    payday_map = {
        "Monday": 1,
        "Tuesday": 2,
        "Wednesday": 3,
        "Thursday": 4,
        "Friday": 5,
        "Saturday": 6,
        "Sunday": 7
    }

    payday = guild_pg.get_payday()
    if payday is None:
        await ctx.respond(
            hikari.Embed(
                title=localize("Payday"),
                description=localize("The admins haven't set a payday yet.") + "\n" + localize("You should remind them to set one by running `/admin payday`")
            )
        )
    payday_int = payday_map[payday]

    payday = localize(payday)

    # Finds when the next payday is in the form of a timestamp.
    today = datetime.datetime.today()
    # The payday could be any day of the week, so we need to find the next one.
    while today.weekday() != payday_int:
        today += datetime.timedelta(days=1)

    timestamp = today.timestamp()

    embed = (
        hikari.Embed(
            title="Payday",
            description=localize(
                "Your payday is set to be on %s.<br>That's %s",
                variables=(payday, f"<t:{int(timestamp)}:R>",)
            )
        )
    )

    await ctx.respond(embed=embed)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
