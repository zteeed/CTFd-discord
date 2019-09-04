from typing import List, Optional

import discord
from discord.ext import commands
from discord.utils import get

from bot.constants import BOT_CHANNEL


def get_channel(bot: commands.bot.Bot) -> Optional[discord.channel.TextChannel]:
    for server in bot.guilds:
        for channel in server.channels:
            if str(channel) == BOT_CHANNEL:
                return channel
    return None


def get_emoji(bot: commands.bot.Bot, emoji: str):
    return get(bot.emojis, name=emoji)


def get_command_args(context: commands.context.Context) -> List[str]:
    return context.message.content.strip().split()[1:]
