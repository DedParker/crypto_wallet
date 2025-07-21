from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from config import settings

#синхронизация подключения с постгрес
sync_engine = create_engine(
    url=settings.DATABASE_URL_psycopg2,
    echo=False,
)

sync_session_factory = sessionmaker(sync_engine)


class Base(DeclarativeBase):
    pass

Base.metadata.create_all(sync_engine)