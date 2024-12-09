import lightbulb
# defines the plugin
moneycmds_plugin_name = "money"
moneycmds_plugin = lightbulb.Plugin(moneycmds_plugin_name)
@moneycmds_plugin.command()
# The title of the group and its description
@lightbulb.command(
    name="money",
    name_localizations={
        "en-GB": "money",
        "es-ES": "dinero",
        "fr": "argent"
    },
    description="Use and move your money with these commands.",
    description_localizations={
        "en-GB": "Use and move your money with these commands.",
        "es-ES": "Usa y mueve tu dinero con estos comandos.",
        "fr": "Utilisez et déplacez votre argent avec ces commandes."
    }
)
@lightbulb.implements(lightbulb.SlashCommandGroup)
# This is what you import V to use the group.child
async def money_group(_) -> None:
    pass  # as slash commands cannot have their top-level command run, we simply pass here

# Loads the plugin. (Not the other children to the plugin)
def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(moneycmds_plugin)
# Unloads the plugin. (Not the other children to the plugin)
def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(moneycmds_plugin)
