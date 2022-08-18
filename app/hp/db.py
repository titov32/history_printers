import sqlalchemy as sa
from sqlalchemy import orm
from config import DATABASEURL
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession


metadata = sa.MetaData()
SQLALCHEMY_DATABASE_URL = f'postgresql+asyncpg://{DATABASEURL}'
# for SQLite
# SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False,)

async_session = orm.sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

Base = orm.declarative_base(metadata=metadata)


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session
