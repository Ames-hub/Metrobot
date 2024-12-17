from library.storage import PostgreSQL
from .group import subscriptions_group
from library.botapp import botapp
import lightbulb
import asyncio
import hikari

@subscriptions_group.child
@lightbulb.app_command_permissions(dm_enabled=True)
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
    name="interval",
    name_localizations={
        "en-GB": "interval",
        "es-ES": "intervalo",
        "fr": "intervalle"
    },
    description="The interval (in days) at which to send the money.",
    description_localizations={
        "en-GB": "The interval (in days) at which to send the money.",
        "es-ES": "El intervalo (en días) en el que enviar el dinero.",
        "fr": "L'intervalle (en jours) auquel envoyer l'argent."
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
    name="start",
    name_localizations={
        "en-GB": "start",
        "es-ES": "comenzar",
        "fr": "démarrer"
    },
    description="Starts a regularly timed transaction to send money to another user.",
    description_localizations={
        "en-GB": "Starts a regularly timed transaction to send money to another user.",
        "es-ES": "Inicia una transacción regularmente programada para enviar dinero a otro usuario.",
        "fr": "Démarre une transaction régulièrement programmée pour envoyer de l'argent à un autre utilisateur."
    },
    pass_options=True
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def command(ctx: lightbulb.SlashContext, target_user:hikari.User, interval:int, amount:int) -> None:
    user_pg = PostgreSQL.user(ctx.author.id)
    guild_pg = PostgreSQL.guild(ctx.guild_id)
    localize = guild_pg.localize

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

    # Ensures the interval is at least 1 day
    if interval < 1:
        embed = hikari.Embed(
            title=localize("Invalid Interval"),
            description=localize("The interval must be at least 1 day."),
            color=hikari.Color(0xFF0000)
        )
        await ctx.respond(embed)
        return

    # Ensures the amount is at least 1
    if amount < 1:
        embed = hikari.Embed(
            title=localize("Invalid Amount"),
            description=localize("The amount must be at least 1."),
            color=hikari.Color(0xFF0000)
        )
        await ctx.respond(embed)
        return
    elif amount > 1000000:
        embed = hikari.Embed(
            title=localize("Are you sure that's right?"),
            description=localize("%s is quite a lot. Send in chat \"yes\" to confirm.", (amount,)),
            color=hikari.Color(0xFF0000)
        )
        await ctx.respond(embed)

        try:
            await botapp.wait_for(
                hikari.GuildMessageCreateEvent,
                predicate=lambda event: event.author_id == ctx.author.id and event.content.lower() in ["yes", "si", "oui"],
                timeout=30
            )
        except asyncio.TimeoutError:
            return

    # Starts tracking the subscription
    sub_id = user_pg.start_subscription(target_user.id, interval, amount, starting_guild_id=ctx.guild_id)

    embed = (
        hikari.Embed(
            title=localize("Subscription Started | ID %s", (sub_id,)),
            description=localize(
                "You have started a subscription to send %s every %s days to %s.",
                (amount, interval, target_user.username)
            ),
            color=hikari.Color(0x00FF00)
        )
        .add_field(
            name=localize("How do I cancel my subscription?"),
            value=localize("To cancel your subscription, use the command<br>`/subscriptions cancel subscription_id:%s`.", (sub_id,))
        )
    )

    await ctx.respond(embed)

    # Inform the other user
    await target_user.send(
        hikari.Embed(
            title=localize("Subscription Started | ID %s", (sub_id,)),
            description=localize(
                "A subscription to receive %s every %s days from <@%s> has started.",
                (amount, interval, ctx.author.id)
            ),
            color=hikari.Color(0x00FF00)
        )
        .add_field(
            name=localize("How do I cancel my subscription?"),
            value=localize("To cancel your subscription, use the command<br>`/subscriptions cancel subscription_id:%s`.", (sub_id,))
        )
    )

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
