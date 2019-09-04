from discord.ext import commands

from bot.manage.discord_data import get_emoji


def add_emoji(bot: commands.bot.Bot, to_send: str, emoji: str) -> str:
    custom_emoji = get_emoji(bot, emoji)
    if custom_emoji is not None:
        """ emoji exists as custom """
        return f'{to_send} {custom_emoji}'
    else:
        """ emoji is a general emoji """
        return f'{to_send} :{emoji}:'
