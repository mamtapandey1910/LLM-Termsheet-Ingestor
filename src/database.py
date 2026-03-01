import os
from contextlib import contextmanager
from typing import Generator

import psycopg2
import psycopg2.extras

from .models import TermsheetData

_CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS termsheets (
    id              SERIAL PRIMARY KEY,
    deal_name       TEXT,
    borrower        TEXT,
    lender          TEXT,
    facility_type   TEXT,
    currency        TEXT,
    facility_amount TEXT,
    interest_rate   TEXT,
    maturity_date   TEXT,
    closing_date    TEXT,
    purpose         TEXT,
    covenants       TEXT,
    fees            TEXT,
    raw_text        TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
"""

_INSERT_SQL = """
INSERT INTO termsheets (
    deal_name, borrower, lender, facility_type, currency,
    facility_amount, interest_rate, maturity_date, closing_date,
    purpose, covenants, fees, raw_text
) VALUES (
    %(deal_name)s, %(borrower)s, %(lender)s, %(facility_type)s, %(currency)s,
    %(facility_amount)s, %(interest_rate)s, %(maturity_date)s, %(closing_date)s,
    %(purpose)s, %(covenants)s, %(fees)s, %(raw_text)s
) RETURNING id;
"""


def get_connection_params() -> dict:
    """Build psycopg2 connection parameters from environment variables."""
    return {
        "host": os.environ.get("POSTGRES_HOST", "localhost"),
        "port": int(os.environ.get("POSTGRES_PORT", 5432)),
        "dbname": os.environ.get("POSTGRES_DB", "termsheet_db"),
        "user": os.environ.get("POSTGRES_USER", "postgres"),
        "password": os.environ.get("POSTGRES_PASSWORD", ""),
    }


@contextmanager
def get_connection(**overrides) -> Generator:
    """Context manager that yields an open psycopg2 connection.

    Keyword arguments override the environment-derived connection params.
    The connection is committed and closed on clean exit, rolled back on error.
    """
    params = {**get_connection_params(), **overrides}
    conn = psycopg2.connect(**params)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def ensure_table(conn) -> None:
    """Create the termsheets table if it does not already exist."""
    with conn.cursor() as cur:
        cur.execute(_CREATE_TABLE_SQL)


def insert_termsheet(conn, data: TermsheetData) -> int:
    """Insert a :class:`TermsheetData` record and return the new row id.

    Args:
        conn: An open psycopg2 connection (not yet committed).
        data: The extracted termsheet data to persist.

    Returns:
        The auto-generated primary key of the inserted row.
    """
    with conn.cursor() as cur:
        cur.execute(_INSERT_SQL, data.model_dump(exclude_none=False))
        row_id: int = cur.fetchone()[0]
    return row_id
