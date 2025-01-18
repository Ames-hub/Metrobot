from library.storage import PostgreSQL
from library.botapp import botapp
import lightbulb, hikari

@botapp.listen(lightbulb.CommandErrorEvent)
async def on_error(event: lightbulb.CommandErrorEvent) -> None:
    localize = PostgreSQL.guild(event.context.guild_id).localize

    if isinstance(event.exception, lightbulb.MissingRequiredPermission):
        await event.context.respond(
            localize("You don't have the required permissions to run this command."),
            flags=hikari.MessageFlag.EPHEMERAL
        )
    elif isinstance(event.exception, lightbulb.MissingRequiredRole):
        await event.context.respond(
            localize("You don't have the required role to run this command."),
            flags=hikari.MessageFlag.EPHEMERAL
        )
    elif isinstance(event.exception, lightbulb.BotMissingRequiredPermission):
        await event.context.respond(
            localize("I don't have the required permissions to run this command!"),
            flags=hikari.MessageFlag.EPHEMERAL
        )
    elif isinstance(event.exception, lightbulb.errors.OnlyInDM):
        await event.context.respond(
            localize("This command can only be run in DMs."),
            flags=hikari.MessageFlag.EPHEMERAL
        )
    elif isinstance(event.exception, lightbulb.errors.OnlyInGuild):
        await event.context.respond(
            localize("This command can only be run in a guild."),
            flags=hikari.MessageFlag.EPHEMERAL
        )
    elif isinstance(event.exception, lightbulb.errors.NSFWChannelOnly):
        await event.context.respond(
            localize("This command can only be run in a NSFW channel."),
            flags=hikari.MessageFlag.EPHEMERAL
        )
    elif isinstance(event.exception, lightbulb.errors.NotOwner):
        await event.context.respond(
            localize("You are not the owner of this bot."),
            flags=hikari.MessageFlag.EPHEMERAL
        )
    elif isinstance(event.exception, lightbulb.errors.CommandIsOnCooldown):
        await event.context.respond(
            localize(
                "You have %s seconds left before you can run this command again.",
                variables=(f"{event.exception.retry_after:.2f}",)
                )
        )
    elif isinstance(event.exception, lightbulb.errors.BotOnly):
        await event.context.respond(
            localize("This command can only be run by bots."),
            flags=hikari.MessageFlag.EPHEMERAL
        )
    elif isinstance(event.exception, lightbulb.errors.NotEnoughArguments):
        await event.context.respond(
            localize("We're missing some needed information to run this command!"),
            flags=hikari.MessageFlag.EPHEMERAL
        )
    elif isinstance(event.exception, lightbulb.errors.InvalidArgument):
        await event.context.respond(
            localize("Invalid information to run this command!"),
            flags=hikari.MessageFlag.EPHEMERAL
        )
    elif isinstance(event.exception, lightbulb.errors.MissingRequiredAttachmentArgument):
        await event.context.respond(
            localize("You need to attach a file to run this command."),
            flags=hikari.MessageFlag.EPHEMERAL
        )
    elif isinstance(event.exception, lightbulb.errors.CommandNotFound):
        pass # Ignore this error, since it is not a problem.
    elif isinstance(event.exception, hikari.errors.BadRequestError):
        await event.context.respond(
            localize("There was an error with the request."),
            flags=hikari.MessageFlag.EPHEMERAL
        )
        raise event.exception
    elif isinstance(event.exception, hikari.errors.NotFoundError):
        pass  # Ignore this error, since we can't do anything about it.
    else:
        await event.context.respond(
            localize("An unknown error occured :( Please try again later when the issue is resolved."),
            flags=hikari.MessageFlag.EPHEMERAL
        )
        raise event.exception
    
def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
