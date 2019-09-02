from typing import Any, Tuple

import discord.utils

import bot.manage.channel_data as channel_data
import bot.manage.database_data as database_data
from bot.constants import limit_size, medals


def display_parts(message):
    message = message.split('\n')
    tosend = ''
    stored = []
    for part in message:
        if len(tosend + part + '\n') >= limit_size:
            stored.append(tosend)
            tosend = ''
        tosend += part + '\n'
    stored.append(tosend)
    return stored


def display_scoreboard(bot, all_players=False):
    tosend = ''
    users_data = database_data.get_scoreboard(bot.db.session, bot.db.tables, type='admin')
    if not all_players:
        users_data = users_data[:20]
    for rank, user_data in enumerate(users_data):
        user, score = user_data['username'], user_data['score']
        if rank < len(medals):
            tosend += f'{medals[rank]} {user} --> Score = {score} \n'
        else:
            tosend += f' • • • {user} --> Score = {score} \n'

    return tosend


def display_categories(bot):
    tosend = ''
    categories_data = database_data.get_categories(bot.db.session, bot.db.tables)
    for category in categories_data:
        tosend += f' • {category} \n'
    return tosend


def display_category(category, bot):
    category_info = database_data.get_category_info(bot.db.session, bot.db.tables, category)
    if not category_info:
        tosend = f'Category {category} does not exists.'
        return tosend

    tosend = ''
    for challenge in category_info:
        tosend += f' • {challenge["name"]} ({challenge["value"]} points) \n'
    return tosend


def display_who_solved(bot, challenge_selected):
    if not database_data.challenge_exists(bot.db.session, bot.db.tables, challenge_selected):
        return f'Challenge {challenge_selected} does not exists.'
    tosend = ''
    users = database_data.get_users_solved_challenge(bot.db.session, bot.db.tables, challenge_selected, type='admin')
    for user in users:
        tosend += f' • {user}\n'
    if not tosend:
        tosend = f'Nobody solves {challenge_selected}.'
    return tosend


def display_problem(bot, context, challenge_selected):
    if not database_data.challenge_exists(bot.db.session, bot.db.tables, challenge_selected):
        return f'Challenge {challenge_selected} does not exists.'

    discord_users = database_data.get_authors_challenge(bot.db.session, bot.db.tables, challenge_selected)
    if not discord_users:
        tosend = f'Cannot find authors for challenge "{challenge_selected}".'
        return tosend

    discord_users = [f'{name}#{id}' for (name, id) in discord_users]
    discord_members = []
    for discord_user in discord_users:
        discord_members += [discord.utils.find(lambda u: discord_user == str(u), context.message.guild.members).mention]
    tosend = 'Ping: ' + ' | '.join(discord_members)
    return tosend


def display_last_days(bot, days_num, username):
    if not database_data.user_exists(bot.db.session, bot.db.tables, username):
        tosend = f'User {username} does not exists.'
        tosend_list = [{'user': username, 'msg': tosend}]
        return tosend_list

    challenges_data = database_data.get_challenges_solved_during(bot.db.session, bot.db.tables, days_num)

    tosend_list = []
    for challenge_data in challenges_data:
        username_challenge = challenge_data['username']
        if username is not None and username_challenge != username:
            continue
        challenges = challenge_data['challenges']
        tosend = ''
        for challenge in challenges:
            tosend += f' • {challenge["name"]} ({challenge["value"]} points) - {challenge["date"]}\n'
        tosend_list.append({'user': username_challenge, 'msg': tosend})

    test = [item['msg'] == '' for item in tosend_list]
    if username is not None and False not in test:
        tosend = f'No challenges solved by {username} :frowning:'
        tosend_list = [{'user': None, 'msg': tosend}]
    elif False not in test:
        tosend = 'No challenges solved by anyone :frowning:'
        tosend_list = [{'user': None, 'msg': tosend}]

    return tosend_list


def display_diff(bot, user1, user2):
    if not database_data.user_exists(bot.db.session, bot.db.tables, user1):
        tosend = f'User {user1} does not exists.'
        tosend_list = [{'user': user1, 'msg': tosend}]
        return tosend_list
    if not database_data.user_exists(bot.db.session, bot.db.tables, user2):
        tosend = f'User {user2} does not exists.'
        tosend_list = [{'user': user2, 'msg': tosend}]
        return tosend_list

    user1_diff, user2_diff = database_data.diff(bot.db.session, bot.db.tables, user1, user2)
    tosend_list = []

    tosend = '\n'.join([f' • {challenge["name"]} ({challenge["value"]} points)' for challenge in user1_diff])
    tosend_list.append({'user': user1, 'msg': tosend})
    tosend = '\n'.join([f' • {challenge["name"]} ({challenge["value"]} points)' for challenge in user2_diff])
    tosend_list.append({'user': user2, 'msg': tosend})

    return tosend_list


async def display_flush(channel, context):
    result = await channel_data.flush(channel)
    if channel is None or not result:
        return 'An error occurs while trying to flush channel data.'
    return f'Data from channel has been flushed successfully by {context.author}.'


async def display_cron(bot: Any) -> Tuple[Any, Any, Any]:
    tag, challenge = database_data.get_new_challenges(bot.db.session, bot.db.tables, bot.db.tag)
    bot.db.tag = tag
    if challenge:
        name = f'New challenge solved by {challenge["username"]}'
        tosend = f' • {challenge["challenge"]} ({challenge["value"]} points)'
        tosend += f'\n • Date: {challenge["date"]}'
        return name, tosend, 0xFFCC00
    challenges_id = bot.db.challenges
    test_challenges_id = database_data.get_visible_challenges(bot.db.session, bot.db.tables)
    if test_challenges_id == challenges_id:
        return None, None, None
    else:
        new_challenges_id = [id for id in test_challenges_id if id not in challenges_id]
        tosend = ''
        for id in new_challenges_id:
            (name, value, category) = database_data.get_challenge_info(bot.db.session, bot.db.tables, id)
            tosend += f' • {name} ({value} points) - category {category}'
        bot.db.challenges = new_challenges_id
        return "New challenge available", tosend, 0x16B841
