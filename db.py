from bot.database.sql import get_sqlalchemy_engine, get_sqlalchemy_session, get_sqlalchemy_tables
from bot.manage.database_data import get_visible_challenges


class Database:

    def __init__(self, db_uri):
        self.engine, self.base = get_sqlalchemy_engine(db_uri)
        self.session = get_sqlalchemy_session(self.engine)
        self.tables = get_sqlalchemy_tables(self.base)
        self.tag = None  # hash of string composed of last challenge solve user id and challenge id
        # list of visible challenges ids
        self.challenges = get_visible_challenges(self.session, self.tables)
