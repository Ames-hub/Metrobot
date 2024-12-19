import lightbulb
# defines the plugin
marketcmds_plugin_name = "market"
marketcmds_plugin = lightbulb.Plugin(marketcmds_plugin_name)
@marketcmds_plugin.command()
# The title of the group and its description
@lightbulb.command(
    name="market",
    name_localizations={
        "en-GB": "market",
        "es-ES": "mercado",
        "fr": "marché"
    },
    description="The market, and all details about it.",
    description_localizations={
        "en-GB": "The market, and all details about it.",
        "es-ES": "El mercado, y todos los detalles sobre él.",
        "fr": "Le marché, et tous les détails à ce sujet."
    }
)
@lightbulb.implements(lightbulb.SlashCommandGroup)
# This is what you import V to use the group.child
async def market_group(_) -> None:
    pass  # as slash commands cannot have their top-level command run, we simply pass here

# Loads the plugin. (Not the other children to the plugin)
def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(marketcmds_plugin)
# Unloads the plugin. (Not the other children to the plugin)
def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(marketcmds_plugin)
