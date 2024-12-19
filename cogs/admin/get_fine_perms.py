import psycopg2.errors

from library.storage import PostgreSQL
from .group import admin_group
import lightbulb
import hikari

@admin_group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.add_cooldown(bucket=lightbulb.buckets.UserBucket, length=5, uses=1)
@lightbulb.add_checks(
    lightbulb.has_guild_permissions(hikari.Permissions.ADMINISTRATOR)
)
@lightbulb.command(
    name="get_fine_perms",
    name_localizations={
        "en-GB": "get_fine_perms",
        "es-ES": "obtener_permisos_multa",
        "fr": "obtenir_permissions_amende"
    },
    description="Get the role with the ability to fine other users.",
    description_localizations={
        "en-GB": "Get the role with the ability to fine other users.",
        "es-ES": "Obtener el rol con la capacidad de multar a otros usuarios.",
        "fr": "Obtenir le rôle avec la capacité d'amender d'autres utilisateurs."
    },
    pass_options=True
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def command(ctx: lightbulb.SlashContext) -> None:
    localize = PostgreSQL.guild(ctx.guild_id).localize

    try:
        role_id = PostgreSQL.guild(ctx.guild_id).get_fine_perms_role()
    except psycopg2.errors.UniqueViolation:
        await ctx.respond(localize("Uh oh, something went wrong!") + " :(")
        return

    await ctx.respond(
        hikari.Embed(
            title=localize("Fine Permissions"),
            description=localize("We have fetched the role with the ability to fine others."),
            color=hikari.Color(0x00FF00),
        )
        .add_field(
            name="Role:",
            value=f"<@&{role_id}>",
        )
    )


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
