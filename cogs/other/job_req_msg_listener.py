from library.storage import PostgreSQL
from library.botapp import botapp
import lightbulb
import hikari

class bot_plugin(lightbulb.Plugin):
    @staticmethod
    @botapp.listen(hikari.events.ReactionAddEvent)
    async def listener(event: hikari.events.ReactionAddEvent) -> None:
        if event.user_id == botapp.d['bot_id']:
            return

        if event.emoji_name == '👍':
            # Check if the message id is a job requirement message
            if PostgreSQL.guild.is_job_req_msg(event.message_id):
                job_msg = PostgreSQL.guild.get_job_request_msg(event.message_id)

                PostgreSQL.user(event.user_id).set_job_for_guild(
                    guild_id=job_msg['guild_id'],
                    job_id=job_msg['job_id']
                )


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
