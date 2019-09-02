import datetime
from typing import Dict, List

import pytest
from sqlalchemy.orm import Session

from bot.database.sql import get_sqlalchemy_engine, get_sqlalchemy_session, get_sqlalchemy_tables
from bot.database.tables import CTFdTables
from bot.manage.database_data import get_ctf_name, get_false_submissions, get_visible_challenges, get_challenge_info, \
    get_scoreboard, get_users, get_categories, get_category_info, user_exists, challenge_exists, \
    get_authors_challenge, get_users_solved_challenge, get_challenges_solved_during, challenges_solved_by_user, diff, \
    track_user


@pytest.fixture
def db_uri() -> str:
    return 'sqlite:///ctfd.db'


@pytest.fixture
def session(db_uri: str) -> Session:
    engine, base = get_sqlalchemy_engine(db_uri)
    return get_sqlalchemy_session(engine)


@pytest.fixture
def tables(db_uri: str) -> CTFdTables:
    engine, base = get_sqlalchemy_engine(db_uri)
    return get_sqlalchemy_tables(base)


@pytest.fixture()
def tables_name() -> List[str]:
    return [
        'alembic_version', 'awards', 'challenges', 'config', 'dynamic_challenge', 'files', 'flags', 'hints',
        'notifications', 'pages', 'solves', 'submissions', 'tags', 'teams', 'tracking', 'unlocks', 'users'
    ]


@pytest.fixture
def columns() -> Dict:
    columns = dict()
    columns['alembic_version'] = [
        'alembic_version.version_num'
    ]
    columns['awards'] = [
        'awards.id', 'awards.user_id', 'awards.team_id', 'awards.type', 'awards.name', 'awards.description',
        'awards.date', 'awards.value', 'awards.category', 'awards.icon', 'awards.requirements'
    ]
    columns['challenges'] = [
        'challenges.id', 'challenges.name', 'challenges.description', 'challenges.max_attempts', 'challenges.value',
        'challenges.category', 'challenges.type', 'challenges.state', 'challenges.requirements'
    ]
    columns['config'] = [
        'config.id', 'config.key', 'config.value'
    ]
    columns['dynamic_challenge'] = [
        'dynamic_challenge.id', 'dynamic_challenge.initial', 'dynamic_challenge.minimum', 'dynamic_challenge.decay'
    ]
    columns['files'] = [
        'files.id', 'files.type', 'files.location', 'files.challenge_id', 'files.page_id'
    ]
    columns['flags'] = [
        'flags.id', 'flags.challenge_id', 'flags.type', 'flags.content', 'flags.data'
    ]
    columns['hints'] = [
        'hints.id', 'hints.type', 'hints.challenge_id', 'hints.content', 'hints.cost', 'hints.requirements'
    ]
    columns['notifications'] = [
        'notifications.id', 'notifications.title', 'notifications.content', 'notifications.date',
        'notifications.user_id', 'notifications.team_id'
    ]
    columns['pages'] = [
        'pages.id', 'pages.title', 'pages.route', 'pages.content', 'pages.draft', 'pages.hidden', 'pages.auth_required'
    ]
    columns['solves'] = [
        'solves.id', 'solves.challenge_id', 'solves.user_id', 'solves.team_id'
    ]
    columns['submissions'] = [
        'submissions.id', 'submissions.challenge_id', 'submissions.user_id', 'submissions.team_id', 'submissions.ip',
        'submissions.provided', 'submissions.type', 'submissions.date'
    ]
    columns['tags'] = [
        'tags.id', 'tags.challenge_id', 'tags.value'
    ]
    columns['teams'] = [
        'teams.id', 'teams.oauth_id', 'teams.name', 'teams.email', 'teams.password', 'teams.secret', 'teams.website',
        'teams.affiliation', 'teams.country', 'teams.bracket', 'teams.hidden', 'teams.banned', 'teams.captain_id',
        'teams.created'
    ]
    columns['tracking'] = [
        'tracking.id', 'tracking.type', 'tracking.ip', 'tracking.user_id', 'tracking.date'
    ]
    columns['unlocks'] = [
        'unlocks.id', 'unlocks.user_id', 'unlocks.team_id', 'unlocks.target', 'unlocks.date', 'unlocks.type'
    ]
    columns['users'] = [
        'users.id', 'users.oauth_id', 'users.name', 'users.password', 'users.email', 'users.type', 'users.secret',
        'users.website', 'users.affiliation', 'users.country', 'users.bracket', 'users.hidden', 'users.banned',
        'users.verified', 'users.team_id', 'users.created'
    ]
    return columns


def test_tables(db_uri: str, tables_name: List[str]):
    engine, base = get_sqlalchemy_engine(db_uri)
    assert tables_name == engine.table_names()


def test_columns(db_uri: str, tables_name: List[str], columns: Dict):
    engine, base = get_sqlalchemy_engine(db_uri)
    for table_name in tables_name:
        table = getattr(base.classes, table_name, None)
        cols = [f'{table_name}.{column.key}' for column in table.__table__.columns]
        assert table is not None
        assert cols == columns[table_name]


def test_ctf_name(session: Session, tables: CTFdTables):
    assert 'zTeeed CTF' == get_ctf_name(session, tables)


def test_false_submissions(session: Session, tables: CTFdTables):
    assert [('zTeeed', 'Challenge2', 'NotTheFlag')] == get_false_submissions(session, tables)


def test_visible_challenges(session: Session, tables: CTFdTables):
    assert [1, 2] == get_visible_challenges(session, tables)


def test_challenge_info(session: Session, tables: CTFdTables):
    assert get_challenge_info(session, tables, 0) is None
    assert ('Challenge1', 50, 'Category1') == get_challenge_info(session, tables, 1)
    assert ('Challenge2', 50, 'Category2') == get_challenge_info(session, tables, 2)
    assert get_challenge_info(session, tables, 3) is None


def test_scoreboard_user(session: Session, tables: CTFdTables):
    scoreboard = get_scoreboard(session, tables, type='user')
    assert [{'username': 'user1', 'score': 50}, {'username': 'user2', 'score': 50}] == scoreboard


def test_scoreboard_admin(session: Session, tables: CTFdTables):
    scoreboard = get_scoreboard(session, tables, type='admin')
    assert [{'username': 'zTeeed', 'score': 50}] == scoreboard


def test_get_users(session: Session, tables: CTFdTables):
    assert ['user1', 'user2'] == get_users(session, tables, type='user')


def test_admins(session: Session, tables: CTFdTables):
    assert ['zTeeed'] == get_users(session, tables, type='admin')


def test_categories(session: Session, tables: CTFdTables):
    assert ['Category1', 'Category2'] == get_categories(session, tables)


def test_category_info(session: Session, tables: CTFdTables):
    assert [{'name': 'Challenge1', 'value': 50}] == get_category_info(session, tables, 'Category1')
    assert [{'name': 'Challenge2', 'value': 50}] == get_category_info(session, tables, 'Category2')
    assert [] == get_category_info(session, tables, 'Category42')


def test_user_exists(session, tables):
    assert True == user_exists(session, tables, 'zTeeed')
    assert True == user_exists(session, tables, 'user1')
    assert False == user_exists(session, tables, 'user42')


def test_challenge_exists(session, tables):
    assert True == challenge_exists(session, tables, 'Challenge1')
    assert False == challenge_exists(session, tables, 'Challenge42')


def test_authors_challenge(session: Session, tables: CTFdTables):
    assert [('SymLiNK', '2835')] == get_authors_challenge(session, tables, 'Challenge1')
    assert [] == get_authors_challenge(session, tables, 'Challenge2')
    assert get_authors_challenge(session, tables, 'Challenge42') is None


def test_users_solved_challenge(session: Session, tables: CTFdTables):
    assert ['user1'] == get_users_solved_challenge(session, tables, 'Challenge1', type='user')
    assert ['zTeeed'] == get_users_solved_challenge(session, tables, 'Challenge1', type='admin')
    assert ['user2'] == get_users_solved_challenge(session, tables, 'Challenge2', type='user')
    assert [] == get_users_solved_challenge(session, tables, 'Challenge2', type='admin')
    assert get_users_solved_challenge(session, tables, 'Challenge42', type='user') is None
    assert get_users_solved_challenge(session, tables, 'Challenge42', type='admin') is None


def test_challenges_solved_during(session: Session, tables: CTFdTables):
    assert get_challenges_solved_during(session, tables, 99999, type='user') == [
        {'username': 'user1',
         'challenges': [{'name': 'Challenge1', 'value': 50, 'date': datetime.datetime(2019, 8, 15, 18, 47, 50, 572382)}]
         },
        {'username': 'user2',
         'challenges': [{'name': 'Challenge2', 'value': 50, 'date': datetime.datetime(2019, 8, 15, 18, 48, 8, 785247)}]
         }
    ]
    assert get_challenges_solved_during(session, tables, 99999, type='admin') == [
        {'username': 'zTeeed',
         'challenges': [{'name': 'Challenge1', 'value': 50, 'date': datetime.datetime(2019, 8, 15, 18, 48, 27, 905696)}]
         }
    ]


def test_challenges_solved_by_user(session, tables):
    assert [{'name': 'Challenge1', 'value': 50}] == challenges_solved_by_user(session, tables, 'zTeeed')
    assert [{'name': 'Challenge1', 'value': 50}] == challenges_solved_by_user(session, tables, 'user1')
    assert [{'name': 'Challenge2', 'value': 50}] == challenges_solved_by_user(session, tables, 'user2')
    assert challenges_solved_by_user(session, tables, 'user42') is None


def test_diff(session, tables):
    assert ([{'name': 'Challenge1', 'value': 50}],
            [{'name': 'Challenge2', 'value': 50}]) == diff(session, tables, 'user1', 'user2')
    assert (None, None) == diff(session, tables, 'user1', 'user42')
    assert ([], []) == diff(session, tables, 'zTeeed', 'user1')
    assert ([{'name': 'Challenge1', 'value': 50}],
            [{'name': 'Challenge2', 'value': 50}]) == diff(session, tables, 'zTeeed', 'user2')


def test_track_user(session, tables):
    assert ['127.0.0.1'] == track_user(session, tables, 'zTeeed')
    assert ['127.0.0.1'] == track_user(session, tables, 'user1')
    assert ['127.0.0.1'] == track_user(session, tables, 'user2')
    assert track_user(session, tables, 'user42') is None
