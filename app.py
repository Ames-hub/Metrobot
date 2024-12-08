import os
os.makedirs('logs', exist_ok=True)

from library.encryption import encryption
from library.storage import var
keys = encryption('library/private.key')

if var.get("token") is None:
    token = input("Please enter bot token: ")
    var.set("token", keys.encrypt(token))

from library.botapp import botapp
import datetime
import logging
import hikari

logging.basicConfig(
    filename=f'logs/{datetime.datetime.now().strftime("%Y-%m-%d")}.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

@botapp.listen()
async def on_ready(event: hikari.events.ShardReadyEvent) -> None:
    botapp.d['bot_id'] = event.my_user.id
    botapp.d['bot_username'] = event.my_user.username
    print(f"Logged in as {botapp.d['bot_username']}!")
    logging.info(f"Logged in as {botapp.d['bot_username']}!")

# Load all cogs
botapp.load_extensions_from("cogs")
botapp.load_extensions_from("cogs/tasks")

botapp.run()