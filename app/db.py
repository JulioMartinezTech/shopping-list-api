# db.py
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import text
import os

DATABASE_URL = os.getenv("DATABASE_URL")
SCHEMA_NAME = "shopping"

engine = create_engine(DATABASE_URL, echo=True)

def create_schema_and_tables():
    with engine.connect() as connection:
        connection.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{SCHEMA_NAME}"'))
        connection.commit()
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session

