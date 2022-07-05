
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy import create_engine
from config import DATABASEURL


metadata = sa.MetaData()
SQLALCHEMY_DATABASE_URL = DATABASEURL
# for SQLite
# SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = orm.declarative_base(metadata=metadata)


