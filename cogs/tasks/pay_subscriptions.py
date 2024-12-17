from library.botapp import tasks, botapp
from library.storage import PostgreSQL
import lightbulb
import datetime
import hikari

@tasks.task(h=12, wait_before_execution=True, auto_start=True)
async def pay_subs() -> None:
    print("Paying subscriptions...")
    subscription_list = PostgreSQL.list_subscriptions()
    for subscription in subscription_list:
        # noinspection PyTypeChecker
        sub_id = subscription["id"]
        amount = subscription["amount"]
        paying_user_id = subscription["paying_user_id"]
        target_user_id = subscription["target_user"]
        interval:int = subscription["interval"]  # in days
        last_payment = subscription["last_payment"]  # POSIX
        starting_guild_id = subscription["starting_guild_id"]

        # Determine if it's time to pay
        last_payment = datetime.datetime.fromtimestamp(last_payment)
        now = datetime.datetime.now()
        # If the last payment was more than the interval ago, pay again
        if (now - last_payment).days >= interval:
            # Pay the subscription
            payment_result = PostgreSQL.user(paying_user_id).bank.send_money(target_user_id, amount)

            paying_user = await botapp.rest.fetch_user(paying_user_id)
            target_user = await botapp.rest.fetch_user(target_user_id)
            localize = PostgreSQL.guild(starting_guild_id).localize

            if payment_result == -1:
                # Out of money


                embed = (
                    hikari.Embed(
                        title=localize("Subscription payment failed"),
                        description=localize("The subscription with the ID %s couldn't be paid!", (sub_id,)),
                        color=hikari.Color(0xFF0000)
                    )
                    .add_field(
                        name=localize("Not enough money"),
                        value=localize("The user %s doesn't have enough money to pay the subscription to %s.", (paying_user.username, target_user.username))
                    )
                )

                try:
                    await paying_user.send(embed)
                except hikari.errors.ForbiddenError:
                    pass
                except hikari.errors.NotFoundError:
                    pass

                try:
                    await target_user.send(embed)
                except hikari.errors.ForbiddenError:
                    pass
                except hikari.errors.NotFoundError:
                    pass

                continue

            # DM Both users that the payment was successful
            embed = (
                hikari.Embed(
                    title=localize("Subscription Paid"),
                    description=localize(
                        "The subscription between %s and %s was paid successfully (amount: %s).",
                        (paying_user.username, target_user.username, amount)),
                    color=hikari.Color(0x00FF00)
                )
                .add_field(
                    name=localize("How do I cancel my subscription?"),
                    value=localize("To cancel your subscription, use the command<br>`/subscriptions cancel subscription_id:%s`.", (sub_id,))
                )
            )

            try:
                await paying_user.send(embed)
            except hikari.errors.ForbiddenError:
                pass
            except hikari.errors.NotFoundError:
                pass

            try:
                await target_user.send(embed)
            except hikari.errors.ForbiddenError:
                pass
            except hikari.errors.NotFoundError:
                pass

            # Update the last payment date
            PostgreSQL.update_subscription_paid(sub_id)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
