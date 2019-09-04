from typing import Dict, List, Optional, Tuple

import discord.utils
from discord.ext import commands

import bot.manage.channel_data as channel_data
import bot.manage.database_data as database_data
from bot.constants import LIMIT_SIZE, MEDALS, CATCH_MODE
from bot.display.update import add_emoji
from db import Database


def display_parts(message: str) -> List[str]:
    message = message.split('\n')
    to_send = ''
    stored = []
    for part in message:
        if len(to_send + part + '\n') >= LIMIT_SIZE:
            stored.append(to_send)
            to_send = ''
        to_send += part + '\n'
    stored.append(to_send)
    return stored


def display_scoreboard(db: Database, all_players: bool = False) -> str:
    to_send = ''
    users_data = database_data.get_scoreboard(db.session, db.tables, user_type=CATCH_MODE)
    if not all_players:
        users_data = users_data[:20]
    for rank, user_data in enumerate(users_data):
        user, score = user_data['username'], user_data['score']
        if rank < len(MEDALS):
            to_send += f'{MEDALS[rank]} {user} --> Score = {score} \n'
        else:
            to_send += f' • • • {user} --> Score = {score} \n'

    return to_send


def display_categories(db: Database) -> str:
    to_send = ''
    categories_data = database_data.get_categories(db.session, db.tables)
    for category in categories_data:
        to_send += f' • {category} \n'
    return to_send


def display_category(db: Database, category: str) -> str:
    category_info = database_data.get_category_info(db.session, db.tables, category)
    if not category_info:
        to_send = f'Category {category} does not exists.'
        return to_send

    to_send = ''
    for challenge in category_info:
        to_send += f' • {challenge["name"]} ({challenge["value"]} points) \n'
    return to_send


def display_who_solved(db: Database, challenge_selected: str) -> str:
    if not database_data.challenge_exists(db.session, db.tables, challenge_selected):
        return f'Challenge {challenge_selected} does not exists.'
    to_send = ''
    users = database_data.get_users_solved_challenge(db.session, db.tables, challenge_selected, user_type=CATCH_MODE)
    for user in users:
        to_send += f' • {user}\n'
    if not to_send:
        to_send = f'Nobody solves {challenge_selected}.'
    return to_send


def display_problem(db: Database, context: commands.context.Context, challenge_selected: str) -> str:
    if not database_data.challenge_exists(db.session, db.tables, challenge_selected):
        return f'Challenge {challenge_selected} does not exists.'

    discord_users = database_data.get_authors_challenge(db.session, db.tables, challenge_selected)
    if not discord_users:
        to_send = f'Cannot find authors for challenge "{challenge_selected}".'
        return to_send

    discord_users = [f'{user_name}#{user_id}' for (user_name, user_id) in discord_users]
    discord_members = []
    for discord_user in discord_users:
        discord_members += [discord.utils.find(lambda u: discord_user == str(u), context.message.guild.members)]
    discord_members = [member.mention for member in discord_members if member]
    if not discord_members:
        to_send = f'Cannot find authors for challenge "{challenge_selected}".'
        return to_send
    to_send = 'Ping: ' + ' | '.join(discord_members)
    to_send = add_emoji(context.bot, to_send, 'open_mouth')
    return to_send


def display_last_days(db: Database, days_num: int, username: Optional[str]) -> List[Dict[str, str]]:
    if username is not None and not database_data.user_exists(db.session, db.tables, username, user_type=CATCH_MODE):
        to_send = f'User {username} does not exists.'
        to_send_list = [{'user': username, 'msg': to_send}]
        return to_send_list

    challenges_data = database_data.get_challenges_solved_during(db.session, db.tables, days_num, user_type=CATCH_MODE)

    to_send_list = []
    for challenge_data in challenges_data:
        username_challenge = challenge_data['username']
        if username is not None and username_challenge != username:
            continue
        challenges = challenge_data['challenges']
        to_send = ''
        for challenge in challenges:
            to_send += f' • {challenge["name"]} ({challenge["value"]} points) - {challenge["date"]}\n'
        to_send_list.append({'user': username_challenge, 'msg': to_send})

    test = [item['msg'] == '' for item in to_send_list]
    if username is not None and False not in test:
        to_send = f'No challenges solved by {username} :frowning:'
        to_send_list = [{'user': None, 'msg': to_send}]
    elif False not in test:
        to_send = 'No challenges solved by anyone :frowning:'
        to_send_list = [{'user': None, 'msg': to_send}]

    return to_send_list


def display_diff(db: Database, user1: str, user2: str) -> List[Dict[str, str]]:
    if not database_data.user_exists(db.session, db.tables, user1, user_type=CATCH_MODE):
        to_send = f'User {user1} does not exists.'
        to_send_list = [{'user': user1, 'msg': to_send}]
        return to_send_list
    if not database_data.user_exists(db.session, db.tables, user2, user_type=CATCH_MODE):
        to_send = f'User {user2} does not exists.'
        to_send_list = [{'user': user2, 'msg': to_send}]
        return to_send_list

    user1_diff, user2_diff = database_data.diff(db.session, db.tables, user1, user2, user_type=CATCH_MODE)
    to_send_list = []

    to_send = '\n'.join([f' • {challenge["name"]} ({challenge["value"]} points)' for challenge in user1_diff])
    to_send_list.append({'user': user1, 'msg': to_send})
    to_send = '\n'.join([f' • {challenge["name"]} ({challenge["value"]} points)' for challenge in user2_diff])
    to_send_list.append({'user': user2, 'msg': to_send})

    return to_send_list


async def display_flush(context: commands.context.Context) -> str:
    result = await channel_data.flush(context.message.channel)
    if context.message.channel is None or not result:
        return 'An error occurs while trying to flush channel data.'
    return f'Data from channel has been flushed successfully by {context.message.author}.'


async def display_cron(db: Database) -> Tuple[Optional[str], Optional[str], Optional[int]]:
    tag, challenge = database_data.get_new_challenges(db.session, db.tables, db.tag, user_type=CATCH_MODE)
    db.tag = tag
    if challenge:
        name = f'New challenge solved by {challenge["username"]}'
        to_send = f' • {challenge["challenge"]} ({challenge["value"]} points)'
        to_send += f'\n • Date: {challenge["date"]}'
        return name, to_send, 0xFFCC00
    challenges_id = db.challenges
    test_challenges_id = database_data.get_visible_challenges(db.session, db.tables)
    if (test_challenges_id == challenges_id) or (len(test_challenges_id) < len(challenges_id)):
        db.challenges = test_challenges_id
        return None, None, None
    else:
        new_challenges_id = [id for id in test_challenges_id if id not in challenges_id]
        to_send = ''
        for id in new_challenges_id:
            (name, value, category) = database_data.get_challenge_info(db.session, db.tables, id)
            to_send += f' • {name} ({value} points) - {category}'
        db.challenges = test_challenges_id
        return "New challenge available", to_send, 0x16B841
