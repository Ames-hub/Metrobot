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
    description="The amount to give to the user.",
    description_localizations={
        "en-GB": "The amount to give to the user.",
        "es-ES": "La cantidad a dar al usuario.",
        "fr": "Le montant à donner à l'utilisateur."
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
    description="The user to send money to.",
    description_localizations={
        "en-GB": "The user to send money to.",
        "es-ES": "El usuario al que enviar dinero.",
        "fr": "L'utilisateur à qui envoyer de l'argent."
    },
    type=hikari.OptionType.USER,
    required=True
)
@lightbulb.add_cooldown(bucket=lightbulb.buckets.UserBucket, length=5, uses=1)
@lightbulb.add_checks(
    lightbulb.has_guild_permissions(hikari.Permissions.ADMINISTRATOR)
)
@lightbulb.command(
    name="give_money",
    name_localizations={
        "en-GB": "give_money",
        "es-ES": "dar_dinero",
        "fr": "donner_argent"
    },
    description="Give a user a certain amount of money.",
    description_localizations={
        "en-GB": "Give a user a certain amount of money.",
        "es-ES": "Dar a un usuario una cierta cantidad de dinero.",
        "fr": "Donner à un utilisateur un certain montant d'argent."
    },
    pass_options=True
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def command(ctx: lightbulb.SlashContext, amount: int, user: hikari.User) -> None:
    target_pg = PostgreSQL.user(user.id)
    target_pg.ensure_user_exists()

    localize = PostgreSQL.guild(ctx.guild_id).localize

    try:
        target_pg.bank.modify_balance(amount, operator="+")
        success = True
    except psycopg2.errors.CheckViolation:
        success = False

    if success:
        await ctx.respond(
            localize(
                "The user has been given %s%s.",
                variables=(localize("$"), amount,)
            )
        )
    else:
        await ctx.respond(
            localize("Uh oh, something went wrong!") + " :("
        )

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
