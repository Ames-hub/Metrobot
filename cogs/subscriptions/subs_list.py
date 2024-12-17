from library.storage import PostgreSQL
from .group import subscriptions_group
import lightbulb
import hikari

@subscriptions_group.child
@lightbulb.app_command_permissions(dm_enabled=True)
@lightbulb.add_cooldown(bucket=lightbulb.buckets.UserBucket, length=3, uses=1)
@lightbulb.command(
    name="list",
    name_localizations={
        "en-GB": "list",
        "es-ES": "lista",
        "fr": "liste"
    },
    description="Lists all the subscriptions you have.",
    description_localizations={
        "en-GB": "Lists all the subscriptions you have.",
        "es-ES": "Enumera todas las suscripciones que tienes.",
        "fr": "Liste toutes les abonnements que vous avez."
    },
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def command(ctx: lightbulb.SlashContext) -> None:
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

    list_str = ""

    for sub_id in sub_list:
        sub = sub_list[sub_id]
        target_user_id = sub['target_user']
        paying_user_id = sub['paying_user_id']
        amount = sub['amount']

        list_str += localize("<@%s> is paying <@%s> %s%s<br>", variables=(paying_user_id, target_user_id, amount, localize("$")))
        list_str += localize(f"Subscription ID: %s<br>", variables=(sub_id,))

    if len(list_str) == 0:
        list_str = localize("You have no subscriptions.")

    embed = (
        hikari.Embed(
            title=localize("Subscriptions"),
            description=list_str,
            color=0x0000FF
        )
    )

    await ctx.respond(embed, flags=hikari.MessageFlag.EPHEMERAL)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
