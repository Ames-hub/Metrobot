from library.storage import PostgreSQL
from library.botapp import botapp
import lightbulb
import hikari

@botapp.command
@lightbulb.app_command_permissions(dm_enabled=True)
@lightbulb.add_cooldown(bucket=lightbulb.buckets.GuildBucket, length=5, uses=1)
@lightbulb.command(
    name="balance",
    name_localizations={
        "en-GB": "balance",
        "es-ES": "saldo",
        "fr": "solde"
    },
    description="Shows the user's balance",
    description_localizations={
        "en-GB": "Shows the user's balance",
        "es-ES": "Muestra el saldo del usuario",
        "fr": "Montre le solde de l'utilisateur"
    },
)
@lightbulb.implements(lightbulb.SlashCommand)
async def command(ctx: lightbulb.SlashContext) -> None:
    user_pg = PostgreSQL.user(ctx.author.id)
    user_pg.ensure_user_exists()
    localise = PostgreSQL.guild(ctx.guild_id).localize
    balance = user_pg.bank.get_balance()

    embed = (
        hikari.Embed(
            title=localise("Balance | Your Bank"),
            description=localise(
                "You have %s%s in your bank account.",
                variables=(localise("$"), balance)
            ),
            colour=botapp.d["colourless"]
        )
        .set_author(name=ctx.author.username, icon=ctx.author.avatar_url)
    )
    await ctx.respond(embed=embed)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
