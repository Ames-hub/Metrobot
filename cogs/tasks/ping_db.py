from library.storage import ConfPostgreSQL
from library.botapp import tasks
import lightbulb

# Occassionally ping the DB to see if we need to use the fallback
@tasks.task(s=45, wait_before_execution=True, auto_start=True)
def ping_db_bot() -> None:
    if ConfPostgreSQL.ping_db() is False:
        if ConfPostgreSQL.start_db() is False:
            ConfPostgreSQL.make_db_container()
        else:
            if ConfPostgreSQL.ping_db() is False:
                ConfPostgreSQL.make_db_container()
    else:
        pass # DB is up

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
