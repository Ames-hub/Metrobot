import hikari.errors

from library.botapp import tasks, botapp
from library.storage import PostgreSQL
import lightbulb
import datetime

# Occassionally ping the DB to see if we need to use the fallback
@tasks.task(h=12, wait_before_execution=True, auto_start=True)
async def salary_task() -> None:
    guild_list = PostgreSQL.list_guilds()
    for guild_id in guild_list:
        guild_pg = PostgreSQL.guild(guild_id)

        # Example: str(Monday)
        payday = guild_pg.get_payday()
        if payday is None:
            continue

        if not payday == datetime.datetime.now().strftime('%A'):
            return # Not the payday yet

        # Pay everyone in the guild
        member_list = guild_pg.get_known_members()
        job_id_list = []

        for member_id in member_list:
            user_pg = PostgreSQL.user(member_id)
            member = user_pg.fetch_saved_data()

            if member['is_human'] is False:
                continue

            user_pg.ensure_user_exists()

            job_data = user_pg.get_job_for_guild(guild_id)
            job_id = job_data['job_id']
            job_id_list.append(job_id)

            # Gets salary for their job
            salary = PostgreSQL.guild.get_salary(job_id)

            # Pay the user
            user_pg.bank.modify_balance(
                amount=salary,
                operator='+'
            )

        try:
            sys_channel = botapp.d['guild_sys_channels'][guild_id]
        except KeyError:
            guild = await botapp.rest.fetch_guild(guild_id)
            botapp.d['guild_sys_channels'][guild_id] = int(guild.system_channel_id)
            sys_channel = guild.system_channel_id

        # Send a message to the guild, pinging all job roles, that payday has arrived
        payday_message = guild_pg.localize("It's payday! Everyone pinged has been paid.")
        if len(job_id_list) != 0:
            ping_msg = guild_pg.localize("Jobs paid: ")
            for job_id in job_id_list:
                ping_msg += f"<@&{job_id}> "
        else:
            ping_msg = guild_pg.localize("No one was pinged because no one has a job.")
        try:
            await botapp.rest.create_message(
                sys_channel,
                content=f"{payday_message}\n{ping_msg}"
            )
        except hikari.errors.ForbiddenError:
            pass
        except hikari.errors.NotFoundError:
            pass
        except hikari.errors.UnauthorizedError:
            pass

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
