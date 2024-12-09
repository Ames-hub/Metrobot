from library.storage import PostgreSQL
from .group import job_group
import lightbulb
import hikari

@job_group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.add_cooldown(bucket=lightbulb.buckets.UserBucket, length=10, uses=1)
@lightbulb.command(
    name="quit",
    name_localizations={
        "en-GB": "quit",
        "es-ES": "dejar",
        "fr": "quitter"
    },
    description="Quit your current job.",
    description_localizations={
        "en-GB": "Quit your current job.",
        "es-ES": "Deja tu trabajo actual.",
        "fr": "Quittez votre emploi actuel."
    },
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def command(ctx: lightbulb.SlashContext) -> None:
    localize = PostgreSQL.guild(ctx.guild_id).localize

    # Job exists. Check if user already has a job.
    user_pg = PostgreSQL.user(ctx.author.id)
    user_pg.ensure_user_exists()

    success = await user_pg.quit_job(ctx.guild_id)
    if success is True:
        embed = (
            hikari.Embed(
                title=localize("You have quit your job."),
                description=localize("You are now unemployed."),
                color=hikari.Color(0x00FF00)
            )
            .set_author(name=ctx.author.username , icon=ctx.author.avatar_url)
        )
    elif success == -1:
        embed = (
            hikari.Embed(
                title=localize("I don't have permission to remove this role :( Make sure the role's position is lower than mine!"),
                description=localize("You are still employed."),
                color=hikari.Color(0xFF0000)
            )
            .set_author(name=ctx.author.username , icon=ctx.author.avatar_url)
        )
    elif success == -2:
        embed = (
            hikari.Embed(
                title=localize("You don't have a job to quit."),
                description=localize("You are unemployed."),
                color=hikari.Color(0xFF0000)
            )
            .set_author(name=ctx.author.username , icon=ctx.author.avatar_url)
        )
    else:
        embed = (
            hikari.Embed(
                title=localize("We couldn't figure out how to quit?"),
                description=localize("If you were employed, you still are."),
                color=hikari.Color(0xFF0000)
            )
            .set_author(name=ctx.author.username , icon=ctx.author.avatar_url)
        )

    await ctx.respond(embed=embed, flags=hikari.MessageFlag.EPHEMERAL)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
