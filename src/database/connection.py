from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

from dotenv import load_dotenv
from psycopg import connect
from psycopg import sql
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from src.database.models import Base, Product, ProductEvent, ProductUnderlying

if TYPE_CHECKING:
    from src.schema.product_schema import TermsheetExtract

load_dotenv()

REQUIRED_ENV_VARS = ["POSTGRES_HOST", "POSTGRES_PORT", "POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD"]


def _get_db_config() -> dict[str, str]:
    """Get database configuration from environment variables."""
    missing = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
    return {
        "host": os.environ["POSTGRES_HOST"],
        "port": os.environ["POSTGRES_PORT"],
        "database": os.environ["POSTGRES_DB"],
        "user": os.environ["POSTGRES_USER"],
        "password": os.environ["POSTGRES_PASSWORD"],
    }


def get_database_url() -> str:
    configured_url = os.getenv("DATABASE_URL")
    if configured_url:
        return configured_url

    cfg = _get_db_config()
    return f"postgresql+psycopg://{cfg['user']}:{cfg['password']}@{cfg['host']}:{cfg['port']}/{cfg['database']}"


def get_engine() -> Engine:
    return create_engine(get_database_url(), pool_pre_ping=True)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())


def check_database_connection() -> None:
    with get_engine().connect() as connection:
        connection.execute(text("SELECT 1"))


def create_database_if_not_exists() -> None:
    cfg = _get_db_config()

    with connect(
        host=cfg["host"],
        port=cfg["port"],
        dbname="postgres",
        user=cfg["user"],
        password=cfg["password"],
        autocommit=True,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (cfg["database"],))
            exists = cursor.fetchone() is not None
            if not exists:
                cursor.execute(
                    sql.SQL("CREATE DATABASE {}").format(sql.Identifier(cfg["database"]))
                )


def create_tables() -> None:
    Base.metadata.create_all(bind=get_engine())


def save_termsheet(data: "TermsheetExtract") -> Product:
    """Save extracted termsheet data to database. Updates if ISIN already exists."""
    session = SessionLocal()
    try:
        # Check if product with same ISIN exists
        existing_product = session.query(Product).filter(Product.isin == data.isin).first()
        if existing_product:
            raise ValueError(f"Duplicate ISIN detected: {data.isin}. Insertion aborted.")
        # Create new Product
        product = Product(
            isin=data.isin,
            sedol=data.sedol,
            short_description=data.short_description,
            issuer=data.issuer,
            currency=data.currency,
            product_type=data.product_type,
            guarantor=data.guarantor,
            dealer=data.dealer,
            nominal_amount=data.nominal_amount,
            specified_denomination=data.specified_denomination,
            calculation_amount=data.calculation_amount,
            strike_date=data.strike_date,
            issue_date=data.issue_date,
            trade_date=data.trade_date,
            maturity_date=data.maturity_date,
            coupon_barrier_level=data.coupon_barrier_level,
            knock_in_barrier_level=data.knock_in_barrier_level,
        )
        session.add(product)

        # Create ProductEvents
        for event in data.events:
            product_event = ProductEvent(
                product_isin=data.isin,
                event_type=event.event_type,
                event_level_pct=event.event_level_pct,
                event_strike_pct=event.event_strike_pct,
                event_date=event.event_date,
                event_amount=event.event_amount,
                event_payment_date=event.event_payment_date,
            )
            session.add(product_event)

        # Create ProductUnderlyings
        for underlying in data.underlyings:
            product_underlying = ProductUnderlying(
                product_isin=data.isin,
                bbg_code=underlying.bbg_code,
                weight=underlying.weight,
                initial_price=underlying.initial_price,
            )
            session.add(product_underlying)

        session.commit()
        session.refresh(product)
        return product
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
