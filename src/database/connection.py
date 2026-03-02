from __future__ import annotations

import os

from dotenv import load_dotenv
from psycopg import connect
from psycopg import sql
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from src.database.models import Base

load_dotenv()


def get_database_url() -> str:
    configured_url = os.getenv("DATABASE_URL")
    if configured_url:
        return configured_url

    required_vars = [
        "POSTGRES_HOST",
        "POSTGRES_PORT",
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
    ]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        missing = ", ".join(missing_vars)
        raise ValueError(f"Missing required environment variables: {missing}")

    host = os.environ["POSTGRES_HOST"]
    port = os.environ["POSTGRES_PORT"]
    database = os.environ["POSTGRES_DB"]
    user = os.environ["POSTGRES_USER"]
    password = os.environ["POSTGRES_PASSWORD"]

    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{database}"


def get_engine() -> Engine:
    return create_engine(get_database_url(), pool_pre_ping=True)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())


def check_database_connection() -> None:
    with get_engine().connect() as connection:
        connection.execute(text("SELECT 1"))


def create_database_if_not_exists() -> None:
    required_vars = [
        "POSTGRES_HOST",
        "POSTGRES_PORT",
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
    ]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        missing = ", ".join(missing_vars)
        raise ValueError(f"Missing required environment variables: {missing}")

    host = os.environ["POSTGRES_HOST"]
    port = os.environ["POSTGRES_PORT"]
    database = os.environ["POSTGRES_DB"]
    user = os.environ["POSTGRES_USER"]
    password = os.environ["POSTGRES_PASSWORD"]

    with connect(
        host=host,
        port=port,
        dbname="postgres",
        user=user,
        password=password,
        autocommit=True,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database,))
            exists = cursor.fetchone() is not None
            if not exists:
                cursor.execute(
                    sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database))
                )


def create_tables() -> None:
    Base.metadata.create_all(bind=get_engine())
