from typing import Tuple

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

from bot.database.tables import CTFdTables


def get_sqlalchemy_engine(DB_URI: str) \
        -> Tuple[sqlalchemy.engine.base.OptionEngine, sqlalchemy.ext.declarative.api.DeclarativeMeta]:
    Base = automap_base()
    engine = create_engine(DB_URI)
    if 'mysql' in DB_URI:
        # disable sqlalchemy caching for mysql
        engine = engine.execution_options(
            isolation_level="READ COMMITTED"
        )
    Base.prepare(engine, reflect=True)
    return engine, Base


def get_sqlalchemy_session(engine: sqlalchemy.engine.base.OptionEngine) -> sqlalchemy.orm.session.Session:
    return Session(engine)


def get_sqlalchemy_tables(base: sqlalchemy.ext.declarative.api.DeclarativeMeta) -> CTFdTables:
    return CTFdTables(base)
