from library.storage import PostgreSQL
from .group import subscriptions_group
import lightbulb
import hikari

@subscriptions_group.child
@lightbulb.app_command_permissions(dm_enabled=True)
@lightbulb.option(
    name="subscription_id",
    name_localizations={
        "en-GB": "subscription_id",
        "es-ES": "id_de_suscripcion",
        "fr": "id_d_abonnement"
    },
    description="The ID of the subscription to cancel.",
    description_localizations={
        "en-GB": "The ID of the subscription to cancel.",
        "es-ES": "El ID de la suscripción a cancelar.",
        "fr": "L'ID de l'abonnement à annuler."
    },
    type=hikari.OptionType.INTEGER,
    required=True
)
@lightbulb.add_cooldown(bucket=lightbulb.buckets.UserBucket, length=3, uses=1)
@lightbulb.command(
    name="cancel",
    name_localizations={
        "en-GB": "cancel",
        "es-ES": "cancelar",
        "fr": "annuler"
    },
    description="Cancels a subscription.",
    description_localizations={
        "en-GB": "Cancels a subscription.",
        "es-ES": "Cancela una suscripción.",
        "fr": "Annule un abonnement."
    },
    pass_options=True
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def command(ctx: lightbulb.SlashContext, subscription_id:int) -> None:
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

    # Ensures the subscription exists and is owned by the user\
    sub_list = user_pg.list_subscriptions_by_id()
    for sub_id in sub_list:
        sub = sub_list[sub_id]
        if sub['sub_id'] == subscription_id:
            user_pg.cancel_subscription(subscription_id)
            await ctx.respond(localize("The subscription has been cancelled."))

            # Inform the other user that the subscription has been cancelled
            target_user_id = sub['target_user']
            paying_user_id = sub['paying_user_id']

            inform_who = paying_user_id if int(target_user_id) == int(ctx.author.id) else target_user_id

            if inform_who is not None:
                informed_user = await ctx.bot.rest.fetch_user(inform_who)
                await informed_user.send(
                    hikari.Embed(
                        title=localize("Subscription Cancelled"),
                        description=localize(
                            "The subscription for %s%s between you and <@%s> has been cancelled.",
                            variables=(localize("$"), sub['amount'], int(target_user_id if paying_user_id == ctx.author.id else paying_user_id))
                        ),
                        color=0x00FF00
                    )
                )

            return
    else:
        await ctx.respond(localize("The subscription does not exist, or you are not authorized to cancel it."))

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
