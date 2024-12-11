from library.storage import PostgreSQL
from .group import admin_group
import lightbulb
import hikari

@admin_group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    name="enabled",
    name_localizations={
        "en-GB": "enabled",
        "es-ES": "habilitado",
        "fr": "activé"
    },
    description="Whether or not the owner is the only one who can set salaries.",
    description_localizations={
        "en-GB": "Whether or not the owner is the only one who can set salaries.",
        "es-ES": "Si el propietario es el único que puede establecer salarios o no.",
        "fr": "Si le propriétaire est le seul à pouvoir définir les salaires ou non."
    },
    type=hikari.OptionType.BOOLEAN,
    required=True
)
@lightbulb.add_cooldown(bucket=lightbulb.buckets.GuildBucket, length=5, uses=1)
@lightbulb.command(
    name="set_salary_conf",
    name_localizations={
        "en-GB": "set_salary_config",
        "es-ES": "establecer_config_salario",
        "fr": "définir_config_salaire"
    },
    description="Set whether or not the owner is the only one who can set salaries.",
    description_localizations={
        "en-GB": "Set whether or not the owner is the only one who can set salaries.",
        "es-ES": "Establecer si el propietario es el único que puede establecer salarios o no.",
        "fr": "Définir si le propriétaire est le seul à pouvoir définir les salaires ou non."
    },
    pass_options=True
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def command(ctx: lightbulb.SlashContext, enabled:bool) -> None:
    guild_pg = PostgreSQL.guild(ctx.guild_id)
    localize = guild_pg.localize

    if guild_pg.get_owner_set_salary_only():
        if ctx.get_guild().owner_id != ctx.author.id:
            await ctx.respond(
                content=localize("You are not the owner of this server, so you cannot change this setting."),
                flags=hikari.MessageFlag.EPHEMERAL
            )
            return

    success = guild_pg.set_owner_set_salary_only(enabled)

    if success:
        await ctx.respond(
            content=localize("The permissions on who can set salaries has been updated."),
            flags=hikari.MessageFlag.EPHEMERAL
        )
    else:
        await ctx.respond(
            content=localize("Something went wrong. Please try again."),
            flags=hikari.MessageFlag.EPHEMERAL
        )

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
