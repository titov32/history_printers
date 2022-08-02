from sqlalchemy import create_engine
from config import DATABASEURL
from hp import models
from hp.models import Base

SQLALCHEMY_DATABASE_URL = f'postgresql://{DATABASEURL}'
engine = create_engine(SQLALCHEMY_DATABASE_URL)
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

