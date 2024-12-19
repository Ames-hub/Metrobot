# Market System
This is the documentation for the operations of the market system.

# Market Products
This section regards the products that are available in the market.
A Market product is an item in a database, with a number assigned to it,
dictating how much there is of that item.

## Making products
The product table is under the name "items"
The table has the following columns:
- Item_name, Text, Not Null, PK
- Description, Text, Not Null
- Rarity, Integer, check(rarity >= 1 and rarity <= 5), Not Null
- value, Integer, Not Null
- Tradable, Boolean, Not Null

The table 'items_in_shop' dictates how many of each item is in the shop.
It is as follows.
- Item name, Text, Not Null, PK.
- Amount, Integer, Not Null

To make a product, you'd have to insert a row into the items table.
The bot would then, once per day, randomize the stock of the shop using items
in the items table.

## Shop product randomization
The shop randomizes its stock once per 6 hours. The stock is randomized by
the `random.choice` module, and the stock is then inserted into the items_in_shop table.

It does this by marking the store as "closed" in botapp.d and then running the
randomization sequence, looping through each item once with a random amount of
what's in stock. It could fall anywhere from 1 to 20 of each item.

## User-added products.
Users can add products to the shop by using the `additem` command.
These items are global and can be bought by anyone.

## User trading
Users can trade items with each other using the `trade` command.
This requires them each to enter an item name, and a quantity of that item.
The bot will then check if the user has the item and its quantity, and if the other user has
what they want to trade for and its quantity. If both users have the items,
the trade will go through.
