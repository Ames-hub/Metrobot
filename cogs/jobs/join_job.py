from library.botapp import botapp
from library.storage import PostgreSQL
from .group import job_group
import lightbulb
import hikari

@job_group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    name="jobrole",
    name_localizations={
        "en-GB": "title",
        "es-ES": "título",
        "fr": "titre"
    },
    description="The role for the job.",
    description_localizations={
        "en-GB": "The role for the job.",
        "es-ES": "El rol para el trabajo.",
        "fr": "Le rôle pour le travail."
    },
    type=hikari.OptionType.ROLE,
    required=True
)
@lightbulb.add_cooldown(bucket=lightbulb.buckets.UserBucket, length=30, uses=1)
@lightbulb.command(
    name="get",
    name_localizations={
        "en-GB": "get",
        "es-ES": "obtener",
        "fr": "obtenir"
    },
    description="Get a new job.",
    description_localizations={
        "en-GB": "Get a new job.",
        "es-ES": "Obtener un nuevo trabajo.",
        "fr": "Obtenir un nouveau travail."
    },
    pass_options=True
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def command(ctx: lightbulb.SlashContext, jobrole:hikari.Role) -> None:
    localize = PostgreSQL.guild(ctx.guild_id).localize
    guild_pg = PostgreSQL.guild(ctx.guild_id)
    guild_pg.ensure_guild_exists()

    job = guild_pg.get_job(jobrole.id)

    if job is None:
        await ctx.respond(localize("That job does not exist."), flags=hikari.MessageFlag.EPHEMERAL)
        return

    # Job exists. Check if user already has a job.
    user_pg = PostgreSQL.user(ctx.author.id)
    user_pg.ensure_user_exists()
    user_pg.save_user(
        username=ctx.author.username,
        avatar_url=ctx.author.avatar_url,
        is_human=(ctx.author.is_bot or ctx.author.is_system) is False,
        guild_id=ctx.guild_id
    )
    job_data = user_pg.get_job_for_guild(ctx.guild_id)

    if job_data is not None:
        # Check if the guild allows multiple jobs.
        if not guild_pg.allows_multiple_jobs():
            await ctx.respond(localize("You already have a job."), flags=hikari.MessageFlag.EPHEMERAL)
            return
        else:
            await ctx.respond(localize("Unfortunately, multi-job support is not yet implemented."), flags=hikari.MessageFlag.EPHEMERAL)
            return
    else:
        # Check if the job is restricted.
        if job['is_restricted_job']:
            # Send a request to the admins to see if they can join.
            result = await PostgreSQL.user(ctx.author.id).request_job_access(ctx.guild_id, jobrole.id)

            if result is True:
                await ctx.respond(localize("Your application to join this job has been sent!"), flags=hikari.MessageFlag.EPHEMERAL)
                return
            else:
                await ctx.respond(
                    localize("We couldn't send your application to join this job.") + "\n" + localize("Have the admins set up the job requests system properly?"),
                    flags=hikari.MessageFlag.EPHEMERAL
                )
                return

        # User does not have a job in this guild. Assign the job.
        try:
            await botapp.rest.add_role_to_member(
                ctx.guild_id,
                ctx.author.id,
                jobrole.id
            )
        except hikari.errors.ForbiddenError:
            await ctx.respond(localize("I don't have permission to assign you this role :( Make sure the role's position is lower than mine!"))
            return

        user_pg.set_job_for_guild(ctx.guild_id, jobrole.id)
        await ctx.respond(localize("You are now a %s.", variables=(jobrole.name,)))

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
