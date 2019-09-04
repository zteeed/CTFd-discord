from bot.constants import CTFD_MODE


class CTFdError(Exception):
    pass


def check_database(Base):
    tables_name = [
        'alembic_version', 'awards', 'challenges', 'config', 'dynamic_challenge', 'files', 'flags', 'hints',
        'notifications', 'pages', 'solves', 'submissions', 'tags', 'teams', 'tracking', 'unlocks', 'users'
    ]
    for table_name in tables_name:
        if not hasattr(Base.classes, table_name):
            raise CTFdError()


class CTFdTables:

    def __init__(self, Base):
        check_database(Base)
        #  self.alembic_version = Base.classes.alembic_version
        #  self.awards = Base.classes.awards
        self.challenges = Base.classes.challenges
        self.config = Base.classes.config
        self.dynamic_challenge = Base.classes.dynamic_challenge
        #  self.files = Base.classes.files
        #  self.flags = Base.classes.flags
        #  self.hints = Base.classes.hints
        #  self.notifications = Base.classes.notifications
        #  self.pages = Base.classes.pages
        self.solves = Base.classes.solves
        self.submissions = Base.classes.submissions
        #  self.tags = Base.classes.tags
        #  self.teams = Base.classes.teams
        self.tracking = Base.classes.tracking
        #  self.unlocks = Base.classes.unlocks
        if CTFD_MODE == 'users':
            self.users = Base.classes.users
        elif CTFD_MODE == 'teams':
            self.users = Base.classes.teams
        else:
            raise CTFdError()
