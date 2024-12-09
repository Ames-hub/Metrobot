from library.storage import PostgreSQL
from library.botapp import botapp
import lightbulb
import hikari

@botapp.command
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.add_cooldown(bucket=lightbulb.buckets.GuildBucket, length=5, uses=1)
@lightbulb.command(
    name="leaderboard",
    name_localizations={
        "en-GB": "leaderboard",
        "es-ES": "tablero",
        "fr": "classement"
    },
    description="Shows the top 10 users in the leaderboard",
    description_localizations={
        "en-GB": "Shows the top 10 users in the leaderboard",
        "es-ES": "Muestra los 10 mejores usuarios en el tablero de clasificación",
        "fr": "Affiche les 10 meilleurs utilisateurs du classement"
    },
)
@lightbulb.implements(lightbulb.SlashCommand)
async def command(ctx: lightbulb.SlashContext) -> None:
    leaderboard = PostgreSQL.get_leaderboard()
    localise = PostgreSQL.guild(ctx.guild_id).localize

    # Gets the top 10 users
    if len(leaderboard) > 10:
        leaderboard = leaderboard[:10]

    embed = (
        hikari.Embed(  # TODO: Localize me to the guild's language
            title=localise("Leaderboard"),
            description=localise("Top 10 users in the leaderboard"),
            colour=botapp.d["colourless"]
        )
    )

    leaderboard_string = f"**__{localise('! WORLD-WIDE LEADERBOARD !')}__**"
    leaderboard_value = "=" * len(leaderboard_string) + "\n"

    # Formats the leaderboard
    for user_id in leaderboard:
        user_pg = PostgreSQL.user(user_id=user_id)
        user_data = user_pg.fetch_saved_data()
        if user_data is None:
            # Fetch the user data from the API
            user_data = await ctx.bot.rest.fetch_user(user_id)
            user_data = {
                "id": user_data.id,
                "username": user_data.username,
                "avatar_url": user_data.avatar_url
            }
            user_pg.save_user(
                username=user_data["username"],
                avatar_url=user_data["avatar_url"]
            )

        leaderboard_value += f"{user_data['username']} - {localise("$")}{leaderboard[user_id]}\n"

    embed.add_field(name=leaderboard_string, value=leaderboard_value)
    await ctx.respond(embed=embed)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
