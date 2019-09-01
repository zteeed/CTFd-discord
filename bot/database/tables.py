class CTFdTables:

    def __init__(self, Base):
        tables_name = [
            'alembic_version', 'awards', 'challenges', 'config', 'dynamic_challenge', 'files', 'flags', 'hints',
            'notifications', 'pages', 'solves', 'submissions', 'tags', 'teams', 'tracking', 'unlocks', 'users'
        ]
        self.all = {}
        for table_name in tables_name:
            if not hasattr(Base.classes, table_name):
                continue
            self.all[table_name] = getattr(Base.classes, table_name)
            setattr(self, table_name, self.all[table_name])
