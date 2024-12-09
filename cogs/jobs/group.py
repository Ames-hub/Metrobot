import lightbulb
# defines the plugin
jobcmds_plugin_name = "job"
jobcmds_plugin = lightbulb.Plugin(jobcmds_plugin_name)
@jobcmds_plugin.command()
# The title of the group and its description
@lightbulb.command(
    name="job",
    name_localizations={
        "en-GB": "job",
        "es-ES": "trabajo",
        "fr": "emploi"
    },
    description="Commands for managing your job(s)",
    description_localizations={
        "en-GB": "Commands for managing your job(s)",
        "es-ES": "Comandos para gestionar tu(s) trabajo(s)",
        "fr": "Commandes pour gérer votre(s) emploi(s)"
    }
)
@lightbulb.implements(lightbulb.SlashCommandGroup)
# This is what you import V to use the group.child
async def job_group(_) -> None:
    pass  # as slash commands cannot have their top-level command run, we simply pass here

# Loads the plugin. (Not the other children to the plugin)
def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(jobcmds_plugin)
# Unloads the plugin. (Not the other children to the plugin)
def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(jobcmds_plugin)
