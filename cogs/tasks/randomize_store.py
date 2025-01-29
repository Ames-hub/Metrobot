from library.storage import ConfPostgreSQL
from library.botapp import tasks
import lightbulb
import logging
import random

@tasks.task(s=45, wait_before_execution=False, auto_start=True)
def randomize_store() -> None:
    conn = ConfPostgreSQL.get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT uuid, item_name FROM items")
        items = cursor.fetchall()

        # format uuids into a list
        item_uuids = [item[0] for item in items]
        # format item names into a list
        item_names = [item[1] for item in items]

        for uuid, name in zip(item_uuids, item_names):
            # Update stock in items_in_shop to be a random number between 10 and 100
            stock_numb = random.randint(10, 100)
            cursor.execute('''
                INSERT INTO items_in_shop (item_uuid, stock, item_name)
                VALUES (%s, %s, %s)
                ON CONFLICT (item_uuid) DO UPDATE SET stock = EXCLUDED.stock;
            ''', (uuid, stock_numb, name))
            conn.commit()
    finally:
        cursor.close()
        conn.close()

    logging.info("Store randomized.")

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
