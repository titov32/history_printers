import sqlalchemy as sa
from sqlalchemy import orm
from app.config import DATABASEURL
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession


metadata = sa.MetaData()
SQLALCHEMY_DATABASE_URL = f'postgresql+asyncpg://{DATABASEURL}'

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False,)

async_session = orm.sessionmaker(engine,
                                 expire_on_commit=False,
                                 class_=AsyncSession)

Base = orm.declarative_base(metadata=metadata)


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)