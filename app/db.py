from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


Base = declarative_base()


def create_session_factory(database_url: str, echo: bool = False):
    engine = create_engine(database_url, echo=echo, future=True)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    return engine, session_factory
