from library.storage import PostgreSQL
from .group import money_group
import lightbulb
import hikari

@money_group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    name="amount",
    name_localizations={
        "en-GB": "amount",
        "es-ES": "cantidad",
        "fr": "montant"
    },
    description="The amount of money to send.",
    description_localizations={
        "en-GB": "The amount of money to send.",
        "es-ES": "La cantidad de dinero a enviar.",
        "fr": "Le montant d'argent à envoyer."
    },
    type=hikari.OptionType.INTEGER,
    required=True
)
@lightbulb.option(
    name="target_user",
    name_localizations={
        "en-GB": "target_user",
        "es-ES": "usuario_objetivo",
        "fr": "utilisateur_cible"
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
@lightbulb.add_cooldown(bucket=lightbulb.buckets.UserBucket, length=3, uses=1)
@lightbulb.command(
    name="send",
    name_localizations={
        "en-GB": "send",
        "es-ES": "enviar",
        "fr": "envoyer"
    },
    description="Send money to another user.",
    description_localizations={
        "en-GB": "Send money to another user.",
        "es-ES": "Envía dinero a otro usuario.",
        "fr": "Envoyer de l'argent à un autre utilisateur."
    },
    pass_options=True
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def command(ctx: lightbulb.SlashContext, target_user:hikari.User, amount:int) -> None:
    user_pg = PostgreSQL.user(ctx.author.id)
    localize = PostgreSQL.guild(ctx.guild_id).localize

    # Ensures both users are in the database
    user_pg.ensure_user_exists()
    user_pg.save_user(
        username=ctx.author.username,
        avatar_url=ctx.author.avatar_url,
        is_human=(ctx.author.is_bot or ctx.author.is_system) is False,
        guild_id=ctx.guild_id
    )
    target_pg = PostgreSQL.user(target_user.id)
    target_pg.ensure_user_exists()
    target_pg.save_user(
        username=target_user.username,
        avatar_url=target_user.avatar_url,
        is_human=(target_user.is_bot or target_user.is_system) is False,
        guild_id=ctx.guild_id
    )

    if target_user.id == ctx.author.id:
        embed = hikari.Embed(
            title=localize("Invalid User"),
            description=localize("You can't send money to yourself."),
            color=hikari.Color(0xFF0000)
        )
        await ctx.respond(embed)
        return
    elif target_user.is_bot:
        embed = hikari.Embed(
            title=localize("Invalid User"),
            description=localize("You can't send money to a bot."),
            color=hikari.Color(0xFF0000)
        )
        await ctx.respond(embed)
        return

    result_success = user_pg.bank.send_money(
        target_id=target_user.id,
        amount=amount
    )

    if result_success is True:
        embed = hikari.Embed(
            title=localize("Money Sent"),
            description=localize(
                text=f"Successfully sent %s coins to %s.",
                variables=(amount, f"<@{target_user.id}>")
            ),
            color=hikari.Color(0x00FF00)
        )
    elif result_success == -1:
        embed = hikari.Embed(
            title=localize("Insufficient Funds"),
            description=localize("You don't have enough money to send that amount."),
            color=hikari.Color(0xFF0000)
        )
    else:
        embed = hikari.Embed(
            title=localize("Money not Sent"),
            description=localize("Something went wrong and the money was not sent."),
            color=hikari.Color(0x0000FF)
        )

    await ctx.respond(embed)

    # Send a message to the target user
    if result_success is True:
        await target_user.send(
            content=(
                hikari.Embed(
                    title=localize("Money Received"),
                    description=localize(
                        text=f"You have received %s coins from %s.",
                        variables=(amount, str(ctx.author.username))
                    ),
                    color=hikari.Color(0x00FF00)
                )
            )
        )

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
