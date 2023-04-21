from sqlalchemy import create_engine, MetaData, select, insert
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
import os
from pathlib import Path

""" Database connection notes:
- Must use psycopg2-binary for postgresql
- Must use snowflake.sqlalchemy for snowflake
"""
path = Path(__file__).parent.parent.joinpath('.env')

load_dotenv(path)

LOCAL_POSTGRES_USR = os.environ['LOCAL_POSTGRES_USR']

LOCAL_POSTGRES_PWD = os.environ[
    'LOCAL_POSTGRES_PWD'
]

LOCAL_POSTGRES_DB = os.environ['LOCAL_POSTGRES_DB']

LOCAL_DATABASE_URL = f"postgresql://{LOCAL_POSTGRES_USR}:{LOCAL_POSTGRES_PWD}@localhost:5432/{LOCAL_POSTGRES_DB}"


engine = create_engine(
    LOCAL_DATABASE_URL,
    pool_size=200,
    echo=True,
)

SessionLocal: sessionmaker = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base(bind=engine)
