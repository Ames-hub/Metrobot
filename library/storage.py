from library.encryption import encryption
import subprocess
import psycopg2
import inspect
import logging
import secrets
import hikari
import json
import time
import os

key_seperator = '.'
settings_path = 'settings.json'
DEBUG = bool(os.environ.get("DEBUG", False))
postgre_port = 10432
db_container_name = "metrobot_db"

keys = encryption(key_file='library/private.key')

class dt:
    SETTINGS = {
        "token": None,
        "db": {
            "host": None,
            "port": None,
            "username": None,
            "password": None,
            "database": None
        }
    }

# noinspection PyTypeChecker
class var:
    @staticmethod
    def set(key, value, file=settings_path, dt_default=dt.SETTINGS) -> bool:
        """
        Sets the value of a key in the memory file.

        :param key: The key to set the value of.
        :param value: The value to set the key to.
        :param file: The file to set the key in.
        :param dt_default: The default dictionary to fill a json file with if the file does not exist.
        :return:
        """
        # Logs the file it creates, and which file and line called it.
        if DEBUG is True:
            logging.info(f'file \'{file}\' was set by {inspect.stack()[1].filename}:{inspect.stack()[1].lineno}')

        keys = str(key).split(key_seperator)
        file_dir = os.path.dirname(file)
        if file_dir == '':
            file_dir = os.getcwd()

        if os.path.exists(file) is False:
            os.makedirs(file_dir, exist_ok=True)
            with open(file, 'w+') as f:
                json.dump(dt_default, f, indent=4, separators=(',', ':'))

        with open(file, 'r+') as f:
            data = json.load(f)

        temp = data
        for k in keys[:-1]:
            if k not in temp:
                temp[k] = {}
            temp = temp[k]

        temp[keys[-1]] = value

        with open(file, 'w+') as f:
            json.dump(data, f, indent=4)

        return True

    @staticmethod
    def get(key, default=None, dt_default=dt.SETTINGS, file=settings_path) -> any:
        """
        Gets the value of a key in the memory file.

        :param key: The key to get the value of.
        :param default: The default value to return if the key does not exist.
        :param dt_default: The default dictionary to fill a json file with if the file does not exist.
        :param file: The file to get the key from.
        Set to None if you want to raise an error if the file does not exist.
        """
        # Logs the file it creates, and which file and line called it.
        if DEBUG is True:
            caller = f"{inspect.stack()[1].filename}:{inspect.stack()[1].lineno}"
            logging.info(f'file \'{file}\' was retrieved from by {caller}')

        keys = str(key).split(key_seperator)
        file_dir = os.path.dirname(file)
        if file_dir == '':
            file_dir = os.getcwd()

        if os.path.exists(file) is True:
            with open(file, 'r+') as f:
                data = dict(json.load(f))
        else:
            if dt_default is not None:
                os.makedirs(file_dir, exist_ok=True)
                with open(file, 'w+') as f:
                    json.dump(dt_default, f, indent=4, separators=(',', ':'))
            else:
                raise FileNotFoundError(f"file '{file}' does not exist.")

            with open(file, 'r+') as f:
                data = dict(json.load(f))

        temp = data
        try:
            for k in keys[:-1]:
                if k not in temp:
                    return default
                temp = temp[k]

            return temp[keys[-1]]
        except KeyError as err:
            logging.error(f"key '{key}' not found in file '{file}'.", err)
            raise KeyError(f"key '{key}' not found in file '{file}'.")

    @staticmethod
    def delete(key, file=settings_path, default=dt.SETTINGS):
        """
        Delete a key.

        :param key: The key to delete.
        :param file: The file to delete the key from.
        :param default: The default dictionary to fill a json file with if the file does not exist.
        """
        # Logs the file it creates, and which file and line called it.
        if DEBUG is True:
            caller = f"{inspect.stack()[1].filename}:{inspect.stack()[1].lineno}"
            logging.info(f'file \'{file}\' was had a key deleted by {caller}')

        keys = str(key).split(key_seperator)
        file_dir = os.path.dirname(file)
        if file_dir == '':
            file_dir = os.getcwd()

        if os.path.exists(file) is True:
            with open(file, 'r+') as f:
                data = dict(json.load(f))
        else:
            if default is not None:
                os.makedirs(file_dir, exist_ok=True)
                with open(file, 'w+') as f:
                    json.dump(default, f, indent=4, separators=(',', ':'))
            else:
                raise FileNotFoundError(f"file '{file}' does not exist.")

            with open(file, 'r+') as f:
                data = dict(json.load(f))

        temp = data
        for k in keys[:-1]:
            if k not in temp:
                return False
            temp = temp[k]

        if keys[-1] in temp:
            del temp[keys[-1]]
            with open(file, 'w+') as f:
                json.dump(data, f, indent=4)
            return True
        else:
            return False

    @staticmethod
    def load_all(file: str = settings_path, dt_default={}) -> dict:
        """
        Load all the keys in a file. Returns a dictionary with all the keys.
        :param file: The file to load all the keys from.
        :param dt_default:
        :return:
        """
        # Logs the file it creates, and which file and line called it.
        if DEBUG is True:
            logging.info(
                f'file \'{file}\' was fully loaded by {inspect.stack()[1].filename}:{inspect.stack()[1].lineno}')

        os.makedirs(os.path.dirname(file), exist_ok=True)
        if not os.path.exists(file):
            with open(file, 'w+') as f:
                json.dump(dt_default, f, indent=4, separators=(',', ':'))

        with open(file, 'r+') as f:
            data = dict(json.load(f))

        return data

    @staticmethod
    def fill_json(file: str = settings_path, data=dt.SETTINGS):
        """
        Fill a json file with a dictionary.
        :param file: The file to fill with data.
        :param data: The data to fill the file with.
        """
        # Logs the file it creates, and which file and line called it.
        if DEBUG is True:
            logging.info(
                f'file \'{file}\' was filled with data by {inspect.stack()[1].filename}:{inspect.stack()[1].lineno}')

        if "/" in file or "\\" in file:
            os.makedirs(os.path.dirname(file), exist_ok=True)
        with open(file, 'w+') as f:
            json.dump(data, f, indent=4, separators=(',', ':'))

        return True

class ConfPostgreSQL:
    @staticmethod
    def modernize():
        # Using this dict, it formats the SQL query to create the tables if they don't exist
        table_dict = {
            # Table name
            'preferred_language': {
                # Column name: Column properties
                'guild_id': 'BIGINT NOT NULL PRIMARY KEY',
                'language': 'TEXT NOT NULL DEFAULT \'en\'',  # Default language is English. This is to prevent errors if the language is not set.
            },
            'user_data': {
                # Data saved about the user so we don't have to spam discord with requests
                'user_id': 'BIGINT NOT NULL PRIMARY KEY',
                'avatar_url': 'TEXT DEFAULT NULL',
                'username': 'TEXT NOT NULL',
                'is_human': 'BOOLEAN DEFAULT TRUE',
            },
            # Used by run_payday.py to get all the members of a guild
            'user_in_guilds': {
                'user_id': 'BIGINT NOT NULL PRIMARY KEY',
                'guild_id': 'BIGINT NOT NULL',
            },
            'user_bank': {
                'user_id': 'BIGINT NOT NULL PRIMARY KEY references user_data(user_id)',
                'balance': 'BIGINT DEFAULT 0 check(balance >= 0)',
            },
            'users_inventory': {
                'user_id': 'BIGINT NOT NULL PRIMARY KEY REFERENCES user_data(user_id)',
                'item_name': 'TEXT NOT NULL',
                'quantity': 'BIGINT DEFAULT 0',
            },
            'items': {
                'item_name': 'TEXT PRIMARY KEY',
                'description': 'TEXT DEFAULT NULL',
                # The levels are: 1 - Common, 2 - Uncommon, 3 - Rare, 4 - Epic, 5 - Legendary, 6 - Truly Unique
                'rarity': 'INTEGER DEFAULT 1 check(rarity >= 1 and rarity <= 5)',
                'value': 'BIGINT DEFAULT 0',
                'tradable': 'BOOLEAN NOT NULL DEFAULT TRUE',
            },
            'items_in_shop': {
                'item_name': 'TEXT PRIMARY KEY REFERENCES items(item_name)',
                'stock': 'BIGINT DEFAULT 0',
            },
            'trade_market_items': {
                'item_name': 'TEXT PRIMARY KEY',
                'description': 'TEXT DEFAULT NULL',
                'price': 'BIGINT DEFAULT 0',
                'seller_id': 'BIGINT NOT NULL REFERENCES user_data(user_id)',
                'timestamp': 'BIGINT DEFAULT extract(epoch from now())::BIGINT',
            },
            "job_roles": {
                "guild_id": "BIGINT NOT NULL",
                "role_id": "BIGINT NOT NULL UNIQUE PRIMARY KEY",
                "is_restricted_job": "BOOLEAN NOT NULL DEFAULT FALSE",
                "is_officer_role": "BOOLEAN NOT NULL DEFAULT FALSE",
                "salary": "BIGINT NOT NULL",
            },
            "multijob_guilds": {
                "guild_id": "BIGINT NOT NULL PRIMARY KEY",
                "allowed": "BOOLEAN NOT NULL DEFAULT FALSE",
            },
            "user_jobs": {
                "started_timestamp": "BIGINT DEFAULT extract(epoch from now())::BIGINT",
                "user_id": "BIGINT NOT NULL PRIMARY KEY",
                "guild_id": "BIGINT NOT NULL",
                "job_id": "BIGINT NOT NULL",
            },
            "job_request_channels": {
                "guild_id": "BIGINT NOT NULL PRIMARY KEY",
                "channel_id": "BIGINT NOT NULL UNIQUE",
            },
            "job_requests": {
                "user_id": "BIGINT NOT NULL",
                "guild_id": "BIGINT NOT NULL",
                "job_id": "BIGINT NOT NULL",
                "timestamp": "BIGINT DEFAULT extract(epoch from now())::BIGINT",
            },
            "job_request_msgs": {
                "msg_id": "BIGINT NOT NULL PRIMARY KEY",
                "guild_id": "BIGINT NOT NULL",
                "channel_id": "BIGINT NOT NULL",
                "user_id": "BIGINT NOT NULL",
                "job_id": "BIGINT NOT NULL",
            },
            "paydays": {
                "guild_id": "BIGINT NOT NULL PRIMARY KEY",
                "payday": "TEXT NOT NULL check(payday in ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'))",
            }
        }

        with ConfPostgreSQL.get_connection() as conn:
            cur = conn.cursor()
            for table_name, columns in table_dict.items():
                # Check if the table exists
                cur.execute('''
                        SELECT EXISTS (
                            SELECT 1
                            FROM information_schema.tables
                            WHERE table_name = %s
                        );
                    ''', (table_name,))
                table_exist = cur.fetchone()[0]

                # If the table exists, check and update columns
                if table_exist:
                    for column_name, column_properties in columns.items():
                        # Check if the column exists
                        cur.execute('''
                                SELECT EXISTS (
                                    SELECT 1
                                    FROM information_schema.columns
                                    WHERE table_name = %s AND column_name = %s
                                );
                            ''', (table_name, column_name))
                        column_exist = cur.fetchone()[0]

                        # If the column doesn't exist, add it
                        if not column_exist:
                            cur.execute(f'ALTER TABLE {table_name} ADD COLUMN {column_name} {column_properties};')

                # If the table doesn't exist, create it with columns
                else:
                    columns_str = ', '.join([f'{column_name} {column_properties}' for column_name, column_properties in columns.items()])
                    cur.execute(f'CREATE TABLE {table_name} ({columns_str});')

            # Commit the changes
            conn.commit()

    @staticmethod
    def check_db_container() -> bool | int:
        """
        Checks if the PostgreSQL container exists and is running.
        :return: True if the container is running, False if it is not running, and -1 if it does not exist.
        """
        # Checks if the PostgreSQL container exists and is running
        try:
            result = subprocess.run(
                ["docker", "inspect", "--format='{{json .State.Status}}'", db_container_name],
                capture_output=True, text=True
            )
        except subprocess.CalledProcessError:
            # Container does not exist
            return -1

        # Weird as heck output
        if result.stdout == '\'"running"\'\n':
            return True
        elif result.stderr != f"Error: No such object \"{db_container_name}\"\n":
            return -1
        else:
            return False

    @staticmethod
    def ping_db():
        try:
            conn = psycopg2.connect(**ConfPostgreSQL.get_details())
            conn.close()
            return True
        except psycopg2.OperationalError:
            return False

    @staticmethod
    def get_connection() -> psycopg2.extensions.connection:
        try:
            return psycopg2.connect(**ConfPostgreSQL.get_details())
        except psycopg2.OperationalError as err:
            # Try to start up the docker container for the database
            if not ConfPostgreSQL.start_db():

                msg = 'Could not reach the database, and when I tried to start the PostgreSQL container, It failed.'
                logging.error(msg, exc_info=True)
                print(msg)

                print("Now attempting to pair with a newly-created local database as a fallback.")
                success = ConfPostgreSQL.make_db_container()
                # Wait a bit for the database to start up
                time.sleep(2)
                if not success:
                    msg = 'Could not pair with a local database.'
                    logging.error(msg)
                    print(msg)
                    exit(1)
                else:
                    print("Successfully paired with a local database.")
                    return psycopg2.connect(**ConfPostgreSQL.get_details())

            msg = 'The database is starting up. Please wait.'
            print(msg)
            logging.info(msg)

            if f'database "{db_container_name}" does not exist' in str(err):
                # Create the database if it doesn't exist
                ConfPostgreSQL.make_main_schema()

            # Wait for the database to start up
            time_waited = 0
            while not ConfPostgreSQL.ping_db():
                # If the database does not start up in 10 seconds, raise an error
                if time_waited > 10:
                    logging.error('The database did not start up in time.')
                    raise err
                time_waited += 1
                time.sleep(1)
            return psycopg2.connect(**ConfPostgreSQL.get_details())

    @staticmethod
    def start_db() -> bool:
        """
        Starts the PostgreSQL container.
        :return: True if the container was started, False if it was not started.
        """
        try:
            subprocess.run(
                ["docker", "start", f"{db_container_name}"],
                check=True,
            )
            return True
        except subprocess.CalledProcessError:
            logging.error('Could not start the container.', exc_info=True)
            return False

    @staticmethod
    def make_db_container() -> bool | None:
        """
        Makes a PostgreSQL container that the DB can use.
        :return: True if the container was created, False if it was not created. None if Docker is not installed.
        """
        # Uses docker to make a PostgreSQL container
        postgres_password = secrets.token_urlsafe(32)

        # Run the Docker container
        try:
            subprocess.run(
                [
                    "docker", "run", "--name", f"{db_container_name}",
                    "-e", f"POSTGRES_PASSWORD={postgres_password}",
                    "-p", f"{postgre_port}:5432",
                    '--restart', 'unless-stopped',
                    "-d", "postgres"
                ],
                check=True,
            )
        except subprocess.CalledProcessError as err:
            logging.error(f'Could not create the container. {err}', )
            return False
        except FileNotFoundError:
            logging.error('Docker is not installed.')
            return None

        print("Waiting for the DB to start...")
        time.sleep(3)
        # Create the PostgreSQL schema/database
        ConfPostgreSQL.make_main_schema()

        # Set the password in the secrets file
        ConfPostgreSQL.save_details({
            'host': '127.0.0.1',
            'port': postgre_port,
            'username': 'postgres',
            'password': postgres_password,
            'database': f'{db_container_name}'
        })

        time.sleep(2)

        ConfPostgreSQL().modernize()

        return True

    @staticmethod
    def make_main_schema():
        # Create the PostgreSQL schema/database
        try:
            subprocess.run(
                [
                    "docker", "exec", "-i", f"{db_container_name}",
                    "psql", "-U", "postgres",
                    "-c", f"CREATE DATABASE {db_container_name};"
                ],
                check=True,
            )
        except subprocess.CalledProcessError as err:
            logging.error('Could not create the database on PostgreSQL.', err)
            return False

    @staticmethod
    def save_details(details: dict):
        """
        Saves the details of the PostgreSQL database to the secrets file.
        :param details: The details to save.
        """
        var.set(file='settings.json', key='db.host', value=details['host'])
        var.set(file='settings.json', key='db.port', value=details['port'])
        var.set(file='settings.json', key='db.username', value=details['username'])
        var.set(file='settings.json', key='db.password', value=keys.encrypt((details['password'])))
        var.set(file='settings.json', key='db.database', value=details['database'])

    @staticmethod
    def get_details() -> dict:
        """
        Returns the details of the PostgreSQL database.
        """
        return {
            'host': var.get('db.host'),
            'port': var.get('db.port'),
            'database': var.get('db.database'),
            'user': var.get('db.username'),
            'password': keys.decrypt((var.get('db.password'))),
        }

class bank:
    def __init__(self, owner_id_of_bank):
        self.owner_id = owner_id_of_bank

    def get_balance(self) -> int | None:
        """
        Get the balance of the bank account.

        :return: Int, the balance of the bank account.
        """
        with ConfPostgreSQL.get_connection() as conn:
            cur = conn.cursor()
            cur.execute('SELECT balance FROM user_bank WHERE user_id = %s;', (self.owner_id,))
            data = cur.fetchone()
            return data[0]

    def modify_balance(self, amount:int, operator:str) -> bool:
        """
        Modify the balance of the bank account.

        :param amount: The amount to modify the balance by.
        :param operator: The operator to use to modify the balance.
        """
        # Handle the operator and create the query
        if operator in ['+', '-', '*', '/']:
            query = f'UPDATE user_bank SET balance = balance {operator} %s WHERE user_id = %s;'
        elif operator in ['=', '==']:
            query = 'UPDATE user_bank SET balance = %s WHERE user_id = %s;'
        else:
            raise ValueError(f'Invalid operator: {operator}')
        
        # Execute the query
        with ConfPostgreSQL.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, (amount, self.owner_id))
            conn.commit()
        return True

    def send_money(self, target_id:int, amount:int) -> bool | int:
        """
        Send money to another bank account.

        :param target_id: The ID of the bank account to send money to.
        :param amount: The amount of money to send.

        :return: True if the money was sent, False if the target account does not exist, and -1 if the balance is too low.
        -2 if the target is the same as the owner.
        """
        if self.owner_id == target_id:
            return -2

        if self.get_balance() >= amount:
            self.modify_balance(amount, '-')
            PostgreSQL.user(target_id).bank.modify_balance(amount, '+')
        else:
            return -1

        return True

class PostgreSQL:
    @staticmethod
    def get_leaderboard() -> dict:
        """
        Get the leaderboard of the bank accounts.

        :returns dict: The leaderboard of the bank accounts.
        Formatted as {user_id: balance}
        """
        with ConfPostgreSQL.get_connection() as conn:
            cur = conn.cursor()
            cur.execute('SELECT user_id, balance FROM user_bank ORDER BY balance DESC;')
            data = cur.fetchall()

        return {user_id: balance for user_id, balance in data}

    @staticmethod
    def list_guilds():
        """
        List all the guilds in the database.
        """
        with ConfPostgreSQL.get_connection() as conn:
            cur = conn.cursor()
            cur.execute('SELECT guild_id FROM preferred_language;')
            data = cur.fetchall()

        return [guild_id for guild_id, in data]

    class user:
        def __init__(self, user_id: int):
            self.user_id = int(user_id)
            self.bank = bank(self.user_id)

        async def request_job_access(self, guild_id, job_id) -> bool:
            """
            Request access to a job in a guild.

            :param guild_id: The ID of the guild.
            :param job_id: The ID of the job.
            """
            try:
                with ConfPostgreSQL.get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute('''
                        INSERT INTO job_requests (user_id, guild_id, job_id)
                        VALUES (%s, %s, %s);
                    ''', (self.user_id, guild_id, job_id))
                    conn.commit()
            except psycopg2.errors.UniqueViolation:
                return False

            # Get the guild's job request channel
            guild_pg = PostgreSQL.guild(guild_id)
            guild_pg.ensure_guild_exists()
            localize = guild_pg.localize

            channel_id = guild_pg.get_job_request_channel()

            if channel_id is not None:
                embed = (
                    hikari.Embed(
                        title=localize('Job Request'),
                        description=localize(
                            '<@%s> is requesting access to a job.',
                            variables=(self.user_id,)
                            ),
                        color=0x00FF00
                    )
                    .add_field(
                        name=localize('Approve?'),
                        value=localize('React with %s to approve the request.', variables=("👍",)),
                    )
                )

                from library.botapp import botapp
                msg = await botapp.rest.create_message(
                    channel_id,
                    embed
                )

                try:
                    with ConfPostgreSQL.get_connection() as conn:
                        cur = conn.cursor()
                        cur.execute('''
                            INSERT INTO job_request_msgs (msg_id, guild_id, channel_id, user_id, job_id)
                            VALUES (%s, %s, %s, %s, %s);
                        ''', (msg.id, guild_id, channel_id, self.user_id, job_id))
                        conn.commit()
                except psycopg2.errors.UniqueViolation:
                    return False

                await msg.add_reaction('👍')  # React to the message with a thumbs up to make it easier for admins to approve the request
                return True
            else:
                return False

        def set_job_for_guild(self, guild_id, job_id):
            """
            Set the job of the user in a guild.

            :param guild_id: The ID of the guild.
            :param job_id: The ID of the job.
            """
            guild_id = int(guild_id)
            job_id = int(job_id)
            try:
                with ConfPostgreSQL.get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute('''
                        INSERT INTO user_jobs (user_id, guild_id, job_id)
                        VALUES (%s, %s, %s)
                    ''', (self.user_id, guild_id, job_id))
                    conn.commit()
            except psycopg2.errors.UniqueViolation:
                # Run update instead
                cur.execute('''
                    UPDATE user_jobs
                    SET job_id = %s
                    WHERE user_id = %s AND guild_id = %s;
                ''', (job_id, self.user_id, guild_id))
                conn.commit()


        def get_job_for_guild(self, guild_id):
            """
            Get the job of the user in a guild.

            :param guild_id: The ID of the guild.
            :return: The job of the user in the guild.
            Formatted as {job_id, guild_id, user_id}
            """
            with ConfPostgreSQL.get_connection() as conn:
                cur = conn.cursor()
                cur.execute('''
                    SELECT job_id, guild_id, user_id
                    FROM user_jobs
                    WHERE user_id = %s AND guild_id = %s;
                ''', (self.user_id, guild_id))
                data = cur.fetchone()

            if data is not None:
                return {
                    'job_id': data[0],
                    'guild_id': data[1],
                    'user_id': data[2]
                }
            else:
                return None

        def ensure_user_exists(self) -> bool:
            """
            Ensure the user exists in the database.

            :return: True if the user exists, False if the user does not exist.
            """
            with ConfPostgreSQL.get_connection() as conn:
                cur = conn.cursor()
                cur.execute('SELECT user_id FROM user_data WHERE user_id = %s;', (self.user_id,))
                if cur.fetchone() is None:
                    # Insert the user into the database
                    cur.execute('''
                        INSERT INTO user_data (user_id, username)
                        VALUES (%s, %s);
                    ''', (self.user_id, ''))

                    # Create a bank account for the user
                    cur.execute('''
                        INSERT INTO user_bank (user_id)
                        VALUES (%s);
                    ''', (self.user_id,))
                    conn.commit()
                    return False
                return True

        def save_user(self, username, avatar_url, is_human: bool = True, guild_id: int = None) -> bool:
            """
            Save the user to the database.

            :param username: The username of the user.
            :param avatar_url: The avatar URL of the user.
            :param is_human: Whether the user is a human or not.
            :param guild_id: The ID of the guild the user is in.
            """
            try:
                with ConfPostgreSQL.get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute('''
                        INSERT INTO user_data (user_id, username, avatar_url, is_human)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (user_id) DO UPDATE SET username = %s, avatar_url = %s;
                    ''', (int(self.user_id), str(username), str(avatar_url), bool(is_human), str(username), str(avatar_url)))
                    conn.commit()

                    # IF guild_id is not none, remember the user in the guild
                    if guild_id is not None:
                        cur.execute('''
                            INSERT INTO user_in_guilds (user_id, guild_id)
                            VALUES (%s, %s)
                            ON CONFLICT (user_id) DO NOTHING;
                        ''', (int(self.user_id), int(guild_id)))
                        conn.commit()
            except psycopg2.errors.ForeignKeyViolation:
                return False
            return True

        def fetch_saved_data(self) -> dict | None:
            """
            Fetch the saved data of the user.

            :returns dict: The saved data of the user.
            """
            with ConfPostgreSQL.get_connection() as conn:
                cur = conn.cursor()
                cur.execute(
                    'SELECT user_id, username, avatar_url, is_human FROM user_data WHERE user_id = %s;',
                    (self.user_id,)
                )
                data = cur.fetchone()

            # Formats data
            if data is not None:
                return {
                    'user_id': data[0],
                    'username': data[1],
                    'avatar_url': data[2],
                    'is_human': data[3]
                }
            else:
                return None

    class guild:
        def __init__(self, guild_id):
            self.guild_id = int(guild_id)

            self.lang = None
            self.translations_file = "translations.json"
            self.translations = None

        def get_known_members(self):
            """
            Get the known members of the guild.

            :return: The known members of the guild.
            """
            with ConfPostgreSQL.get_connection() as conn:
                cur = conn.cursor()
                cur.execute('SELECT user_id FROM user_data WHERE user_id IN (SELECT user_id FROM user_in_guilds WHERE guild_id = %s);', (self.guild_id,))
                data = cur.fetchall()

            return [user_id for user_id, in data]

        def list_job_roles(self):
            """
            List all the job roles in the guild.

            :return: The job roles in the guild.
            Formatted as {role_id, role_name, salary, is_restricted_job, is_officer_role}
            """
            with ConfPostgreSQL.get_connection() as conn:
                cur = conn.cursor()
                cur.execute('SELECT role_id, salary, is_restricted_job, is_officer_role FROM job_roles WHERE guild_id = %s;', (self.guild_id,))
                data = cur.fetchall()

            return_data = {}
            for job in data:
                return_data[job[0]] = {
                    'role_id': job[0],
                    'salary': job[1],
                    'is_restricted_job': job[2],
                    'is_officer_role': job[3]
                }

            return return_data

        @staticmethod
        def get_salary(job_id):
            """
            Get the salary of a job.

            :param job_id: The ID of the job.
            :return: The salary of the job.
            """
            try:
                with ConfPostgreSQL.get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute('SELECT salary FROM job_roles WHERE role_id = %s;', (job_id,))
                    data = cur.fetchone()
            except psycopg2.errors.ProgrammingError:
                return None
            return data[0] if data is not None else None

        def set_payday(self, day):
            """
            Set the payday of the guild.

            :param day: The day of the week to pay the users.
            """
            try:
                with ConfPostgreSQL.get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute('''
                        INSERT INTO paydays (guild_id, payday)
                        VALUES (%s, %s)
                        ON CONFLICT (guild_id) DO UPDATE SET payday = %s;
                    ''', (self.guild_id, day, day))
                    conn.commit()
            except psycopg2.errors.UniqueViolation:
                return False
            except psycopg2.errors.CheckViolation:
                return False
            return True

        def get_payday(self) -> str:
            """
            Get the payday of the guild.

            :return: The payday of the guild.
            """
            with ConfPostgreSQL.get_connection() as conn:
                cur = conn.cursor()
                cur.execute('SELECT payday FROM paydays WHERE guild_id = %s;', (self.guild_id,))
                data = cur.fetchone()
            return data[0] if data is not None else None

        @staticmethod
        def is_job_req_msg(msg_id):
            """
            Check if a message is a job request message.

            :param msg_id: The ID of the message.
            :return: True if the message is a job request message, False if the message is not a job request message.
            """
            with ConfPostgreSQL.get_connection() as conn:
                cur = conn.cursor()
                cur.execute('SELECT msg_id FROM job_request_msgs WHERE msg_id = %s;', (msg_id,))
                data = cur.fetchone()

            return data is not None

        @staticmethod
        def get_job_request_msg(msg_id):
            """
            Get a job request message.

            :param msg_id: The ID of the message.
            :return: The job request message.
            Formatted as {msg_id, guild_id, channel_id, user_id, job_id}
            """
            with ConfPostgreSQL.get_connection() as conn:
                cur = conn.cursor()
                cur.execute('''
                    SELECT msg_id, guild_id, channel_id, user_id, job_id
                    FROM job_request_msgs
                    WHERE msg_id = %s;
                ''', (msg_id,))
                data = cur.fetchone()

            if data is not None:
                return {
                    'msg_id': data[0],
                    'guild_id': data[1],
                    'channel_id': data[2],
                    'user_id': data[3],
                    'job_id': data[4]
                }
            else:
                return None

        def get_job_request_channel(self):
            """
            Get the job request channel of the guild.

            :return: The ID of the channel.
            """
            with ConfPostgreSQL.get_connection() as conn:
                cur = conn.cursor()
                cur.execute('SELECT channel_id FROM job_request_channels WHERE guild_id = %s;', (self.guild_id,))
                return cur.fetchone()[0]

        def set_job_request_channel(self, channel_id):
            """
            Set the job request channel of the guild.

            :param channel_id: The ID of the channel.
            """
            try:
                with ConfPostgreSQL.get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute('''
                        INSERT INTO job_request_channels (guild_id, channel_id)
                        VALUES (%s, %s)
                        ON CONFLICT (guild_id) DO UPDATE SET channel_id = %s;
                    ''', (self.guild_id, channel_id, channel_id))
                    conn.commit()
            except psycopg2.errors.UniqueViolation:
                return False
            return True

        def ensure_guild_exists(self) -> bool:
            """
            Ensure the guild exists in the database.

            :return: True if the guild exists, False if the guild does not exist.
            """
            with ConfPostgreSQL.get_connection() as conn:
                cur = conn.cursor()
                cur.execute('SELECT guild_id FROM preferred_language WHERE guild_id = %s;', (self.guild_id,))
                if cur.fetchone() is None:
                    # Insert the guild into the database
                    cur.execute('''
                        INSERT INTO preferred_language (guild_id, language)
                        VALUES (%s, 'en');
                    ''', (self.guild_id,))
                    conn.commit()
                    return False
                return True

        def set_multijob_rule(self, allowed: bool) -> bool:
            """
            Set whether the guild allows multiple jobs.

            :param allowed: Whether the guild allows multiple jobs.
            """
            try:
                with ConfPostgreSQL.get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute('''
                        INSERT INTO multijob_guilds (guild_id, allowed)
                        VALUES (%s, %s)
                        ON CONFLICT (guild_id) DO UPDATE SET allowed = %s;
                    ''', (self.guild_id, allowed, allowed))
                    conn.commit()
                    return True
            except psycopg2.errors.OperationalError:
                return False

        def allows_multiple_jobs(self) -> bool:
            """
            Check if the guild allows multiple jobs.

            :return: True if the guild allows multiple jobs, False if the guild does not allow multiple jobs.
            """
            with ConfPostgreSQL.get_connection() as conn:
                cur = conn.cursor()
                cur.execute('SELECT allowed FROM multijob_guilds WHERE guild_id = %s;', (self.guild_id,))
                return cur.fetchone()[0]

        def get_job(self, role_id) -> dict | None:
            """
            Get a job from the guild.

            :param role_id: The ID of the role.
            :return: The job or None if the job does not exist.
            """
            with ConfPostgreSQL.get_connection() as conn:
                cur = conn.cursor()
                cur.execute('''
                    SELECT role_id, is_officer_role, is_restricted_job
                    FROM job_roles
                    WHERE guild_id = %s AND role_id = %s;
                ''', (self.guild_id, role_id))
                data = cur.fetchone()

            if data is not None:
                return {
                    'role_id': data[0],
                    'is_officer_role': data[1],
                    'is_restricted_job': data[2]
                }
            else:
                return None

        def add_job_role(self, role_id:int, is_officer_role:bool, is_restricted_job:bool, salary:int) -> bool:
            """
            Add a job role to the guild.

            :param role_id: The ID of the role.
            :param is_officer_role: Whether the role is an officer role.
            :param is_restricted_job: Whether the job requires approval from an admin to be assigned.
            :param salary: The salary of the job. This is the amount of money the user gets paid for the job.
            """
            try:
                with ConfPostgreSQL.get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute('''
                        INSERT INTO job_roles (guild_id, role_id, is_officer_role, is_restricted_job, salary)
                        VALUES (%s, %s, %s, %s, %s);
                    ''',
                    (self.guild_id, int(role_id), bool(is_officer_role), bool(is_restricted_job), int(salary))
                    )
                    conn.commit()
                    return True
            except psycopg2.errors.UniqueViolation:
                return False

        def update_job_role(self, role_id: int, is_officer_role: bool, is_restricted_job: bool, salary: int) -> bool | int:
            """
            Update a job role in the guild.

            :param role_id: The ID of the role.
            :param is_officer_role: Whether the role is an officer role.
            :param is_restricted_job: Whether the job requires approval from an admin to be assigned.
            :param salary: The salary of the job. This is the amount of money the user gets paid for the job.

            :return: True if the job was updated, False if something went wrong, and -1 if the job does not exist.
            """
            try:
                # Ensures the role exists
                if self.get_job(role_id) is None:
                    return -1

                # Update the role
                with ConfPostgreSQL.get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute('''
                        UPDATE job_roles
                        SET is_officer_role = %s, is_restricted_job = %s, salary = %s
                        WHERE guild_id = %s AND role_id = %s;
                    ''', (bool(is_officer_role), bool(is_restricted_job), int(salary), int(self.guild_id), int(role_id)))
                    conn.commit()
                    return True

            except psycopg2.errors.UniqueViolation:
                return False
            except psycopg2.errors.ForeignKeyViolation:
                return False

        def set_language(self, language) -> bool:
            """
            Set the language of the guild.

            :param language: The language to set the guild to.
            """
            try:
                with ConfPostgreSQL.get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute('''
                        INSERT INTO preferred_language (guild_id, language)
                        VALUES (%s, %s)
                        ON CONFLICT (guild_id) DO UPDATE SET language = %s;
                    ''', (self.guild_id, language, language))
                    conn.commit()
            except psycopg2.errors.ForeignKeyViolation:
                return False
            return True

        def get_language(self) -> str | None:
            """
            Get the language of the guild.
            """
            try:
                with ConfPostgreSQL.get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute('SELECT language FROM preferred_language WHERE guild_id = %s;', (self.guild_id,))
                    return cur.fetchone()[0]
            except psycopg2.errors.ForeignKeyViolation:
                return None

        def load_translations(self):
            """Load translations from the JSON file if not already loaded."""
            if self.translations is None:
                with open(self.translations_file, 'r', encoding='utf-8') as f:
                    self.translations = json.load(f)

        def localize(self, text, variables: tuple = None) -> str:
            """
            Localize a string to the set language.

            :param text: The text to localize.
            :param variables: The placeholders to replace in the text. Processed in order.
            :return: Translated text or the original if no translation is found.
            """
            self.load_translations()

            # Get the language, fallback to autodetection if not set
            if self.lang is None:
                self.lang = self.get_language()

            # Attempt to get the translation
            try:
                translation:str = self.translations[text][self.lang]

                # Replace placeholders
                if variables is not None:
                    # A placeholder will appear in translation as %s
                    for placeholder in variables:
                        translation = translation.replace('%s', str(placeholder), 1)

                # Replace <br> with newlines
                translation = translation.replace('<br>', '\n')
                return translation
            except KeyError as err:
                logging.error(f"Translation for '{text}' with lang {self.lang} not found.", err)
                # Fallback to the original text if translation or language is missing
                return f"translation failed: {text}"
