import lightbulb
# defines the plugin
subscriptionscmds_plugin_name = "subscriptions"
subscriptionscmds_plugin = lightbulb.Plugin(subscriptionscmds_plugin_name)
@subscriptionscmds_plugin.command()
# The title of the group and its description
@lightbulb.command(
    name="subscriptions",
    name_localizations={
        "en-GB": "subscriptions",
        "es-ES": "suscripciones",
        "fr": "abonnements"
    },
    description="Manage your subscriptions.",
    description_localizations={
        "en-GB": "Manage your subscriptions.",
        "es-ES": "Administra tus suscripciones.",
        "fr": "Gérez vos abonnements."
    }
)
@lightbulb.implements(lightbulb.SlashCommandGroup)
# This is what you import V to use the group.child
async def subscriptions_group(_) -> None:
    pass  # as slash commands cannot have their top-level command run, we simply pass here

# Loads the plugin. (Not the other children to the plugin)
def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(subscriptionscmds_plugin)
# Unloads the plugin. (Not the other children to the plugin)
def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(subscriptionscmds_plugin)
