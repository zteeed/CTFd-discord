from bot.manage.discord_data import get_emoji


def add_emoji(bot, tosend, emoji):
    custom_emoji = get_emoji(bot, emoji)
    if custom_emoji is not None:
        """ emoji exists as custom """
        return f'{tosend} {custom_emoji}'
    else:
        """ emoji is a general emoji """
        return f'{tosend} :{emoji}:'
