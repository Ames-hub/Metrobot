from library.storage import PostgreSQL
from .group import job_group
import lightbulb
import hikari

@job_group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.add_cooldown(bucket=lightbulb.buckets.UserBucket, length=5, uses=1)
@lightbulb.command(
    name="list",
    name_localizations={
        "en-GB": "list",
        "es-ES": "lista",
        "fr": "liste"
    },
    description="List all the jobs available in this server.",
    description_localizations={
        "en-GB": "List all the jobs available in this server.",
        "es-ES": "Lista todos los trabajos disponibles en este servidor.",
        "fr": "Listez tous les emplois disponibles dans ce serveur."
    },
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def command(ctx: lightbulb.SlashContext) -> None:
    guild_pg = PostgreSQL.guild(ctx.guild_id)
    localize = guild_pg.localize
    guild_pg.ensure_guild_exists()

    job_list = guild_pg.list_job_roles()
    job_string = localize("These are the jobs you can potentially get.") + "\n"

    for job_id in job_list:
        job_data = job_list[job_id]

        job_string += f"**<@&{job_data['role_id']}>** - {localize('$')}{job_data['salary']}"

        print(job_data)
        if job_data["is_officer_role"] is True:
            job_string += f" {localize('(Officer Role)')} "

        if job_data["is_restricted_job"] is True:
            job_string += f" {localize('(Restricted Job)')} "

        job_string += "\n"

    embed = (
        hikari.Embed(
            title=localize("Jobs Available"),
            description=job_string,
            color=0x00FF00
        )
    )

    await ctx.respond(embed=embed)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
