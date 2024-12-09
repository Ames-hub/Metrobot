from library.storage import PostgreSQL
from .group import admin_group
import lightbulb
import hikari

@admin_group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    name="channel",
    name_localizations={
        "en-GB": "channel",
        "es-ES": "canal",
        "fr": "chaîne"
    },
    description="The channel for job requirements requests to be sent to.",
    description_localizations={
        "en-GB": "The channel for job requirements requests to be sent to.",
        "es-ES": "El canal para enviar las solicitudes de requisitos de trabajo.",
        "fr": "Le canal où envoyer les demandes de conditions de travail."
    },
    type=hikari.OptionType.CHANNEL,
    required=True
)
@lightbulb.add_cooldown(bucket=lightbulb.buckets.GuildBucket, length=5, uses=1)
@lightbulb.add_checks(
    lightbulb.has_guild_permissions(hikari.Permissions.ADMINISTRATOR)
)
@lightbulb.command(
    name="jobreqchannel",
    name_localizations={
        "en-GB": "jobreqchannel",
        "es-ES": "canalreqtrabajo",
        "fr": "chaînereqtravail"
    },
    description="Set the channel for job requirements requests to be sent to.",
    description_localizations={
        "en-GB": "Set the channel for job requirements requests to be sent to.",
        "es-ES": "Establece el canal para enviar las solicitudes de requisitos de trabajo.",
        "fr": "Définir le canal où envoyer les demandes de conditions de travail."
    },
    pass_options=True
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def command(ctx: lightbulb.SlashContext, channel:hikari.GuildChannel) -> None:
    guild_pg = PostgreSQL.guild(ctx.guild_id)
    localize = guild_pg.localize

    if channel.type != hikari.ChannelType.GUILD_TEXT:
        embed = (
            hikari.Embed(
                title=localize("Invalid Channel Type!"),
                description=localize("The channel must be a text channel."),
                color=0xFF0000  # Red color
            )
        )

        await ctx.respond(embed)
        return

    success = guild_pg.set_job_request_channel(channel.id)

    if success is True:
        embed = (
            hikari.Embed(
                title=localize("Job Requirement Channel Set!"),
                description=localize(
                    "The channel for job requirements requests has been set to %s",
                    variables=(channel.mention,)
                ),
                color=0x00FF00  # Green color
            )
        )
    else:
        embed = (
            hikari.Embed(
                title=localize("Job Requirement Channel Not Set!"),
                description=localize("An error occurred while setting the job requirement channel. Please try again."),
                color=0xFF0000  # Red color
            )
        )

    await ctx.respond(embed)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
