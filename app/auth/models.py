
from app.hp.db import Base, get_db

from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import orm
from fastapi_users_db_sqlalchemy.access_token import (
    SQLAlchemyAccessTokenDatabase,
    SQLAlchemyBaseAccessTokenTableUUID,)

class User(SQLAlchemyBaseUserTableUUID, Base):
    histories = orm.relationship("History", back_populates="author")


class AccessToken(SQLAlchemyBaseAccessTokenTableUUID, Base):
    pass

async def get_user_db(session: AsyncSession = Depends(get_db)):
    yield SQLAlchemyUserDatabase(session, User)


async def get_access_token_db(
    session: AsyncSession = Depends(get_db),):
    yield SQLAlchemyAccessTokenDatabase(session, AccessToken)