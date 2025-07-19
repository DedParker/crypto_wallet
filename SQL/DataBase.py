from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from SQL.Config import settings


sync_engine = create_engine(
    url=settings.DATABASE_URL_psycopg2,
    echo=False,
)

sync_session_factory = sessionmaker(sync_engine)


class Base(DeclarativeBase):
    pass
