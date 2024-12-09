import lightbulb
# defines the plugin
admincmds_plugin_name = "admin"
admincmds_plugin = lightbulb.Plugin(admincmds_plugin_name)
@admincmds_plugin.command()
# The title of the group and its description
@lightbulb.command(
    name="admin",
    name_localizations={
        "en-GB": "admin",
        "es-ES": "modo",
        "fr": "mod"
    },
    description="Admin commands for the bot.",
    description_localizations={
        "en-GB": "Admin commands for the bot.",
        "es-ES": "Comandos de administrador para el bot.",
        "fr": "Commandes d'administrateur pour le bot."
    }
)
@lightbulb.implements(lightbulb.SlashCommandGroup)
# This is what you import V to use the group.child
async def admin_group(_) -> None:
    pass  # as slash commands cannot have their top-level command run, we simply pass here

# Loads the plugin. (Not the other children to the plugin)
def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(admincmds_plugin)
# Unloads the plugin. (Not the other children to the plugin)
def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(admincmds_plugin)
