import hashlib
import ipaddress
import re
import socket
import struct
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from bot.database.tables import CTFdTables


def get_ctf_name(s: Session, tables: CTFdTables) -> str:
    return s.query(tables.config).filter_by(key='ctf_name').first().value


def get_false_submissions(s: Session, tables: CTFdTables) -> List[Dict]:
    query = s.query(tables.users.name, tables.challenges.name, tables.submissions.provided). \
        join(tables.challenges, tables.challenges.id == tables.submissions.challenge_id). \
        join(tables.users, tables.users.id == tables.submissions.user_id). \
        filter(tables.submissions.type == 'incorrect'). \
        group_by(tables.challenges.id). \
        all()
    return query


def get_scoreboard(s: Session, tables: CTFdTables, type: str = 'user') -> List[Dict]:
    scoreboard = s.query(tables.users.name, func.sum(tables.challenges.value).label('score')). \
        join(tables.solves, tables.users.id == tables.solves.user_id). \
        join(tables.challenges, tables.challenges.id == tables.solves.challenge_id). \
        filter(tables.users.type == type). \
        group_by(tables.users.id). \
        all()

    score_list = [dict(username=username, score=score_user) for (username, score_user) in scoreboard]
    return sorted(score_list, key=lambda item: item['score'], reverse=True)


def get_users(s: Session, tables: CTFdTables, type: str = 'user') -> List[str]:
    scoreboard = get_scoreboard(s, tables, type=type)
    return [item['username'] for item in scoreboard]


def get_categories(s: Session, tables: CTFdTables) -> List[str]:
    categories = s.query(tables.challenges.category).distinct().all()
    return sorted([item[0] for item in categories])


def category_exists(s: Session, tables: CTFdTables, category: str) -> bool:
    challenges = s.query(tables.challenges). \
        filter(tables.challenges.category == category).first()
    return challenges is not None


def get_category_info(s: Session, tables: CTFdTables, category_name: str) -> List[Dict]:
    if not category_exists(s, tables, category_name):
        return []
    challenges = s.query(tables.challenges).filter_by(category=category_name). \
        order_by(desc(tables.challenges.value)).all()
    category_info = []
    for challenge in challenges:
        category_info.append(dict(name=challenge.name, value=challenge.value))
    return category_info


def user_exists(s: Session, tables: CTFdTables, user: str) -> bool:
    user = s.query(tables.users).filter(tables.users.name == user).first()
    return user is not None


def challenge_exists(s: Session, tables: CTFdTables, challenge: str) -> bool:
    challenge = s.query(tables.challenges).filter(tables.challenges.name == challenge).first()
    return challenge is not None


def get_authors_challenge(s: Session, tables: CTFdTables, challenge: str) -> List[Tuple[Any, Any]]:
    if not challenge_exists(s, tables, challenge):
        return None
    description = s.query(tables.challenges.description).filter(tables.challenges.name == challenge).first()
    if description is not None:
        description = description[0]
    result = re.findall(r'@(\w+)#(\d+)', description)
    if result:
        return result
    result = re.findall(r'(.*?)#(\d+)', description)
    if not result:
        return result
    return [(name.split(' ')[-1].replace('@', ''), id) for (name, id) in result]


def get_users_solved_challenge(s: Session, tables: CTFdTables, challenge: str, type: str = 'user'):
    if not challenge_exists(s, tables, challenge):
        return None
    users = get_users(s, tables, type=type)
    users_solves = s.query(tables.users.name). \
        join(tables.solves, tables.users.id == tables.solves.user_id). \
        join(tables.challenges, tables.challenges.id == tables.solves.challenge_id). \
        filter(tables.challenges.name == challenge). \
        filter(tables.users.type == type). \
        all()
    users_solves = [item[0] for item in users_solves]
    # sort users by their rank in the scoreboard
    return [user for user in users if user in users_solves]


def get_challenges_solved_during(s: Session, tables: CTFdTables, days: int = 1, type: str = 'user') -> List[Dict]:
    date_reference = (datetime.now() - timedelta(days=days))  # %y-%m-%d %H:%M:%S
    solved_challenges = s.query(tables.submissions). \
        join(tables.users, tables.users.id == tables.submissions.user_id). \
        join(tables.challenges, tables.challenges.id == tables.submissions.challenge_id). \
        filter(tables.users.type == type). \
        filter(tables.submissions.type == 'correct'). \
        filter(tables.submissions.date > date_reference). \
        order_by(desc(tables.submissions.date)). \
        all()
    users = get_users(s, tables, type=type)
    result_challenges_solved = []
    for user in users:
        solved_during_days = [dict(name=solve.challenges.name, value=solve.challenges.value, date=solve.date)
                              for solve in solved_challenges if solve.users.name == user]
        result_challenges_solved.append(dict(username=user, challenges=solved_during_days))
    return result_challenges_solved


def challenges_solved_by_user(s: Session, tables: CTFdTables, user: str) -> Optional[List[Dict]]:
    if not user_exists(s, tables, user):
        return None
    solved_challenges = s.query(tables.submissions). \
        join(tables.users, tables.users.id == tables.submissions.user_id). \
        join(tables.challenges, tables.challenges.id == tables.submissions.challenge_id). \
        filter(tables.users.name == user). \
        filter(tables.submissions.type == 'correct'). \
        order_by(desc(tables.challenges.value)). \
        all()
    return [dict(name=item.challenges.name, value=item.challenges.value) for item in solved_challenges]


def diff(s: Session, tables: CTFdTables, user1: str, user2: str) -> Tuple[List[Dict], List[Dict]]:
    users = get_users(s, tables, type='user') + get_users(s, tables, type='admin')
    if user1 not in users or user2 not in users:
        return None, None
    user1, user2 = user1.strip(), user2.strip()
    solved_challenges_1 = challenges_solved_by_user(s, tables, user1)
    solved_challenges_2 = challenges_solved_by_user(s, tables, user2)
    all_challs = solved_challenges_1 + solved_challenges_2
    diff1 = [item for item in all_challs if item in solved_challenges_1 and item not in solved_challenges_2]
    diff2 = [item for item in all_challs if item in solved_challenges_2 and item not in solved_challenges_1]
    return diff1, diff2


def track_user(s: Session, tables: CTFdTables, user: str) -> List[str]:
    user = user.strip()
    if not user_exists(s, tables, user):
        return None
    ips = s.query(tables.tracking.ip). \
        join(tables.users, tables.users.id == tables.tracking.user_id). \
        filter(tables.users.name == user). \
        distinct().all()
    ips = [item[0] for item in ips]
    ips = [ip for ip in ips if ipaddress.ip_address(ip).__class__.__name__ == 'IPv4Address']
    return sorted(ips, key=lambda ip: struct.unpack("!L", socket.inet_aton(ip))[0])


def get_challenges_solved(s: Session, tables: CTFdTables) -> List:
    # Changer admin en False plus tard
    challenges = s.query(tables.submissions). \
        join(tables.challenges, tables.challenges.id == tables.submissions.challenge_id). \
        join(tables.users, tables.users.id == tables.submissions.user_id). \
        filter(tables.submissions.type == 'correct'). \
        filter(tables.users.type == 'admin'). \
        order_by(desc(tables.submissions.date)).all()
    return challenges


def get_tag(challenge: Any) -> str:
    tag_value = f'{challenge.users.id} | {challenge.challenges.id}'
    return hashlib.sha224(tag_value.encode()).hexdigest()


def select_challenges_by_tags(challenges: List, tag: str) -> List[Any]:
    selected_challenges = []
    for key, challenge in enumerate(challenges):
        if get_tag(challenge) != tag:
            selected_challenges.append(challenge)
        else:
            return selected_challenges[::-1]  # sort from oldest to newest
    return selected_challenges[::-1]  # sort from oldest to newest


def get_new_challenges(s: Session, tables: CTFdTables, tag: str) -> Tuple[str, Dict]:
    new_challenge = dict()
    new_tag = None
    challenges = get_challenges_solved(s, tables)

    if tag is None:
        if len(challenges) > 0:
            new_tag = get_tag(challenges[0])
        return new_tag, new_challenge

    selected_challenges = select_challenges_by_tags(challenges, tag)
    if len(selected_challenges) > 0:
        item = selected_challenges[0]
        new_tag = get_tag(item)
        new_challenge = dict(username=item.users.name, challenge=item.challenges.name, value=item.challenges.value,
                             date=item.date)
        #  log.debug(f'New solve', username=item.users.name, challenge=item.challenges.name, date=item.date)
        return new_tag, new_challenge
    else:
        return tag, new_challenge
