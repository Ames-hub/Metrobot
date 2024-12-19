import psycopg2.errors

from library.storage import PostgreSQL
from .group import admin_group
import lightbulb
import hikari

@admin_group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    name="amount",
    name_localizations={
        "en-GB": "amount",
        "es-ES": "cantidad",
        "fr": "montant"
    },
    description="The amount to fine the user.",
    description_localizations={
        "en-GB": "The amount to fine the user.",
        "es-ES": "La cantidad para multar al usuario.",
        "fr": "Le montant pour sanctionner l'utilisateur."
    },
    min_value=1,
    type=hikari.OptionType.INTEGER,
    required=True
)
@lightbulb.option(
    name="user",
    name_localizations={
        "en-GB": "user",
        "es-ES": "usuario",
        "fr": "utilisateur"
    },
    description="The user to fine.",
    description_localizations={
        "en-GB": "The user to fine.",
        "es-ES": "El usuario a multar.",
        "fr": "L'utilisateur à sanctionner."
    },
    type=hikari.OptionType.USER,
    required=True
)
@lightbulb.add_cooldown(bucket=lightbulb.buckets.UserBucket, length=5, uses=1)
@lightbulb.command(
    name="fine",
    name_localizations={
        "en-GB": "fine",
        "es-ES": "multar",
        "fr": "sanctionner"
    },
    description="Fine a user a certain amount of money.",
    description_localizations={
        "en-GB": "Fine a user a certain amount of money.",
        "es-ES": "Multar a un usuario una cierta cantidad de dinero.",
        "fr": "Sanctionner un utilisateur d'un certain montant d'argent."
    },
    pass_options=True
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def command(ctx: lightbulb.SlashContext, amount: int, user: hikari.User) -> None:
    target_pg = PostgreSQL.user(user.id)
    target_pg.ensure_user_exists()
    localize = PostgreSQL.guild(ctx.guild_id).localize

    # Checks if the user has admin or a specific role
    user_roles = ctx.member.get_roles()
    permitted_role_id = PostgreSQL.guild(ctx.guild_id).get_fine_perms_role()
    allowed = False
    for role in user_roles:
        if role.id == permitted_role_id:
            allowed = True
            break
        elif hikari.Permissions.ADMINISTRATOR in role.permissions:
            allowed = True
            break

    if not allowed:
        await ctx.respond(localize("You do not have permission to fine users."))

    try:
        target_pg.bank.modify_balance(amount, operator="-")
        success = True
    except psycopg2.errors.CheckViolation:
        success = False

    if not success:
        await ctx.respond(localize("The user does not have enough money to be fined that amount."))
        return

    await ctx.respond(
        localize(
            "The user has been fined %s%s.",
            variables=(localize("$"), amount,)
        )
    )

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
