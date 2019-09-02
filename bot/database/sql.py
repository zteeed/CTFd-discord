from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

from bot.database.tables import CTFdTables
from typing import Any, Tuple


def get_sqlalchemy_engine(db_uri: str) -> Tuple[Any, Any]:
    Base = automap_base()
    engine = create_engine(db_uri)
    engine = engine.execution_options(
        isolation_level="READ COMMITTED"
    )
    Base.prepare(engine, reflect=True)
    return engine, Base


def get_sqlalchemy_session(engine):
    return Session(engine)


def get_sqlalchemy_tables(base):
    return CTFdTables(base)
