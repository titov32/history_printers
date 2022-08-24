from sqlalchemy import create_engine
from config import DATABASEURL, POSTGRESUSER, POSTGRESPASS, POSTGRESDB
from hp import models
from hp.models import Base
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


# Создание БД
try:
    con = psycopg2.connect(f'user={POSTGRESUSER} password={POSTGRESPASS}')
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = con.cursor()
    sqlCreateDatabase = f"create database {POSTGRESDB};"
    cursor.execute(sqlCreateDatabase)
except psycopg2.errors.DuplicateDatabase:
    print('DB created yet')
SQLALCHEMY_DATABASE_URL = f'postgresql://{DATABASEURL}'
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Раскомментируйте ниже строку если нужно очисть БД
# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
