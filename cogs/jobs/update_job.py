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
    description="The title of the job. Gotten from a discord role's name.",
    description_localizations={
        "en-GB": "The title of the job. Gotten from a discord role's name.",
        "es-ES": "El título del trabajo. Obtenido del nombre de un rol de discord.",
        "fr": "Le titre du travail. Obtenu à partir du nom d'un rôle discord."
    },
    type=hikari.OptionType.ROLE,
    required=True
)
@lightbulb.option(
    name="salary",
    name_localizations={
        "en-GB": "salary",
        "es-ES": "salario",
        "fr": "salaire"
    },
    description="The salary of the job.",
    description_localizations={
        "en-GB": "The salary of the job.",
        "es-ES": "El salario del trabajo.",
        "fr": "Le salaire du travail."
    },
    type=hikari.OptionType.INTEGER,
    required=True
)
@lightbulb.option(
    name="is_officer_role",
    name_localizations={
        "en-GB": "officer_role",
        "es-ES": "rol_oficial",
        "fr": "rôle_officier"
    },
    description="Is this job meant to have the authority of a police officer?",
    description_localizations={
        "en-GB": "Is this job meant to have the authority of a police officer?",
        "es-ES": "¿Este trabajo está destinado a tener la autoridad de un oficial de policía?",
        "fr": "Ce travail est-il censé avoir l'autorité d'un officier de police?"
    },
    type=hikari.OptionType.BOOLEAN,
    required=False,
    default=False
)
@lightbulb.option(
    name="is_restricted_job",
    name_localizations={
        "en-GB": "restricted_job",
        "es-ES": "trabajo_restringido",
        "fr": "travail_restrictif"
    },
    description="Does this job require approval from an admin to be assigned?",
    description_localizations={
        "en-GB": "Does this job require approval from an admin to be assigned?",
        "es-ES": "¿Este trabajo requiere aprobación de un admin para ser asignado?",
        "fr": "Ce travail nécessite-t-il l'approbation d'un admin pour être assigné?"
    },
    type=hikari.OptionType.BOOLEAN,
    required=False,
    default=False
)
@lightbulb.add_cooldown(bucket=lightbulb.buckets.GuildBucket, length=5, uses=1)
@lightbulb.add_checks(
    lightbulb.has_guild_permissions(hikari.Permissions.ADMINISTRATOR)
)
@lightbulb.command(
    name="update",
    name_localizations={
        "en-GB": "update",
        "es-ES": "actualizar",
        "fr": "actualiser"
    },
    description="Update an existing job role.",
    description_localizations={
        "en-GB": "Update an existing job role.",
        "es-ES": "Actualiza un rol de trabajo existente.",
        "fr": "Mettre à jour un rôle de travail existant."
    },
    pass_options=True
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def command(ctx: lightbulb.SlashContext, is_officer_role:bool, jobrole:hikari.Role, salary:int, is_restricted_job:bool) -> None:
    localize = PostgreSQL.guild(ctx.guild_id).localize
    guild_pg = PostgreSQL.guild(ctx.guild_id)
    guild_pg.ensure_guild_exists()

    do_prompt_not_owner = False
    if guild_pg.get_owner_set_salary_only():
        if ctx.get_guild().owner_id != ctx.author.id:
            salary = 0
            do_prompt_not_owner = True

    success = guild_pg.update_job_role(
        role_id=jobrole.id,
        is_officer_role=is_officer_role,
        is_restricted_job=is_restricted_job,
        salary=salary
    )

    if success is True:
        if do_prompt_not_owner:
            await ctx.respond(
                content=localize("Job Updated!<br>"
                                 "Note: Only the owner can set salaries, so the salary was defaulted to 0."),
                flags=hikari.MessageFlag.EPHEMERAL
            )
            return
        await ctx.respond(
            content=localize("Job Updated!"),
            flags=hikari.MessageFlag.EPHEMERAL
        )
    elif success == -1:
        await ctx.respond(
            content=localize("That job does not exist."),
            flags=hikari.MessageFlag.EPHEMERAL
        )
    else:
        await ctx.respond(
            content=localize("Uh oh, something went wrong!"),
            flags=hikari.MessageFlag.EPHEMERAL
        )

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
