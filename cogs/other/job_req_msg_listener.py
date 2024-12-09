from library.storage import PostgreSQL
from library.botapp import botapp
import lightbulb
import hikari

class bot_plugin(lightbulb.Plugin):
    @staticmethod
    @botapp.listen(hikari.events.ReactionAddEvent)
    async def mod_listener(event: hikari.events.ReactionAddEvent) -> None:
        user_pg = PostgreSQL.user(event.user_id)
        saved_data = user_pg.fetch_saved_data()
        if saved_data is not None:
            if saved_data["is_human"] is False:
                return
        else:
            if event.user_id in botapp.d['getting_user_data']:
                return
            botapp.d['getting_user_data'].append(event.user_id)
            user = await botapp.rest.fetch_user(event.user_id)
            user_pg.save_user(
                username=user.username,
                avatar_url=user.avatar_url,
                is_human=(user.is_bot or user.is_system) is False
            )
            if user.is_bot or user.is_system:
                return
            botapp.d['getting_user_data'].remove(event.user_id)

        if event.emoji_name == '👍':
            # Check if the message id is a job requirement message
            if PostgreSQL.guild.is_job_req_msg(event.message_id):
                # If the user doesn't already have a job, assign it
                job_msg = PostgreSQL.guild.get_job_request_msg(event.message_id)

                # Delete the job request message
                PostgreSQL.guild(job_msg['guild_id']).delete_job_req_msg(event.message_id)

                await PostgreSQL.user(event.user_id).request_job_confirmation(
                    job_id=job_msg['job_id'],
                    guild_id=job_msg['guild_id']
                )

    @staticmethod
    @botapp.listen(hikari.events.DMReactionAddEvent)
    async def applicant_listener(event: hikari.events.DMReactionAddEvent):
        user_pg = PostgreSQL.user(event.user_id)
        saved_data = user_pg.fetch_saved_data()
        if saved_data is not None:
            if saved_data["is_human"] is False:
                return
        else:
            if event.user_id in botapp.d['getting_user_data']:
                return
            botapp.d['getting_user_data'].append(event.user_id)
            user = await botapp.rest.fetch_user(event.user_id)
            user_pg.save_user(
                username=user.username,
                avatar_url=user.avatar_url,
                is_human=(user.is_bot or user.is_system) is False
            )
            if user.is_bot or user.is_system:
                return
            botapp.d['getting_user_data'].remove(event.user_id)

        if event.emoji_name == '✅':
            if user_pg.msg_id_is_job_req_msg(event.message_id):
                await user_pg.accept_restricted_job(message_id=event.message_id)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
