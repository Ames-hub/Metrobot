## Description

This bot is designed to automate and manage a role-based payment system for your Discord server. It allows you to assign different roles to members, and based on their role, they will receive automatic weekly or daily payments. The bot also includes additional features such as item trading, fines, and subscription management, making it a comprehensive solution for role-based economies within a server.

## Features

### Core Features

- **Role-Based Paycheck System**: Users with specific roles (e.g., "Firefighter", "Police") receive automatic payments based on their assigned role. Payments can be configured on a weekly or daily basis.
- **Send/Receive Money**: Users can send and receive money to each other.
- **Money Leaderboard**: Displays the top earners in the server.
- **Job Restrictions**: Option to restrict users from holding multiple jobs at once (configurable by admins).
- **Basic Shop**: A shop system where users can buy items with in-game currency.
- **Item Trading System**: Allows users to trade items between each other.

### Additional Features

- **Subscriptions**: Users can subscribe to recurring payments (e.g., car insurance), which are automatically deducted from their bank accounts each week.
- **Dual Identity Cards**: Each user can have two identity cards (for different countries, e.g., Spain and France).
- **History Access**: Certain roles (e.g., Police) have access to a log that tracks users' illegal activities.
- **Fine System**: Users can be fined for breaking rules or failing to pay debts.
- **Blacklist System**: Temporarily bans users from joining sessions for a specified amount of time.
- **Forced Payments**: Enables certain actions where a user must pay for items (e.g., buying a car from a dealership).
- **Bank Account**: Each user has a bank account to manage their balance and transactions.
- **French Translation**: The bot can be translated into French for French-speaking servers (configurable).

## Setup Instructions

### Requirements:

- A Discord bot token (create a bot via the [Discord Developer Portal](https://discord.com/developers/applications))
- A Discord server where you want the bot to be installed
- A hosting platform (e.g., Heroku, AWS, or your own server) for the bot to run

### Installation

1. Clone this repository to your local machine or hosting platform.
2. Open a terminal in the directory you cloned it to,
3. Create a virtual environment for Python3.12 (venv)
4. Activate the venv
5. Install the requirements with this command:
    ```
    pip install -r requirements.txt
    ```
6. Run app,py with python with such a command as:
    ```
    python app.py -O
    ```
7. The project will now prompt you for a token.
8. Get a bot token from the [Discord Developer Portal](https://discord.com/developers/applications)
9. Enter the token into the prompt.

And you're all done!
## Commands

### Admin Commands

- `/setpay [role] [amount]`: Set the weekly/daily payment for a specific role.
- `/addfine [user] [amount]`: Fine a user for a rule violation.
- `/ban [user] [duration]`: Temporarily ban a user from joining sessions.
- `/forcepay [user] [amount]`: Force a user to pay for an item (e.g., a car).

### User Commands

- `/balance`: Check your current balance.
- `/send [user] [amount]`: Send money to another user.
- `/subscription request [user] [subscription] [amount]`: Ask another user to begin a subscription (e.g., car insurance).
- `/subscription cancel [user] [subscription]`: Cancel a subscription, as subscriptions must be agreed-upon.
- `/shop`: View the shop and purchase items.
- `/trade [user] [item]`: Trade items with another user.
- `/history`: View your transaction history.

## Contributing

Feel free to fork this repository and submit pull requests to add features or fix bugs. Contributions are welcome!

## Support

If you have any issues or questions, please open an issue on GitHub, and we’ll try to help as soon as possible.