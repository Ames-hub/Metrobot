from library.storage import var, ConfPostgreSQL
from library.encryption import encryption
import os

keys = encryption('library/private.key')
use_debug_token = os.environ.get("USE_DEBUG_TOKEN", False)
if var.get("token") is None:
    token = input("Please enter bot token: ")
    var.set("token", keys.encrypt(token))
if use_debug_token:
    if var.get("debug_token") is None:
        token = input("Please enter debug token: ")
        var.set("debug_token", token)

from library.botapp import botapp
import datetime
import logging
import dotenv
import hikari

dotenv.load_dotenv('.env')

logging.basicConfig(
    filename=f'logs/{datetime.datetime.now().strftime("%Y-%m-%d")}.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

db_container_status = ConfPostgreSQL.check_db_container()
# No container found
if db_container_status == -1:
    ConfPostgreSQL.make_db_container()
elif db_container_status is False:
    ConfPostgreSQL.start_db()

ConfPostgreSQL.modernize()

@botapp.listen()
async def on_ready(event: hikari.events.ShardReadyEvent) -> None:
    botapp.d['bot_id'] = event.my_user.id
    botapp.d['bot_username'] = event.my_user.username
    print(f"Logged in as {botapp.d['bot_username']}!")
    logging.info(f"Logged in as {botapp.d['bot_username']}!")

# Load all cogs
botapp.load_extensions_from("cogs")
botapp.load_extensions_from("cogs/tasks")
botapp.load_extensions_from("cogs/admin")
botapp.load_extensions_from("cogs/other")
botapp.load_extensions_from("cogs/money_cmds")
botapp.load_extensions_from("cogs/subscriptions")
botapp.load_extensions_from("cogs/market")
botapp.load_extensions_from("cogs/jobs")

if bool(os.environ.get("REVEAL_DB_PASS", False)) is True:
    print("Environment variable REVEAL_DB_PASS is set to True")
    print("Database password is:", keys.decrypt(var.get("db.password")))

if bool(os.environ.get("REVEAL_BOT_TOKEN", False)) is True:
    print("Environment variable REVEAL_BOT_TOKEN is set to True")
    if use_debug_token is False:
        print("Bot token is:", keys.decrypt(var.get("token")))
    else:
        print("Bot debug token is:", os.environ.get("debug_token"))

botapp.run()