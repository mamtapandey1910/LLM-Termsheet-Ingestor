"""Unit tests for the PostgreSQL database layer."""

from unittest.mock import MagicMock, call, patch

import pytest

from src.database import ensure_table, get_connection, insert_termsheet
from src.models import TermsheetData

SAMPLE_DATA = TermsheetData(
    deal_name="Project Apollo",
    borrower="Apollo Industries Ltd.",
    lender="Global Capital Bank N.A.",
    facility_type="Senior Secured Term Loan A",
    currency="USD",
    facility_amount="$250,000,000",
    interest_rate="Term SOFR + 2.75%",
    maturity_date="March 31, 2030",
    closing_date="March 31, 2025",
    purpose="Refinancing",
    covenants="Leverage <= 4.0x",
    fees="1% upfront",
    raw_text="raw termsheet text",
)


def _make_mock_conn(row_id: int = 1) -> MagicMock:
    """Return a mock psycopg2 connection whose cursor fetchone returns row_id."""
    mock_cursor = MagicMock()
    mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
    mock_cursor.__exit__ = MagicMock(return_value=False)
    mock_cursor.fetchone.return_value = (row_id,)

    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn


def test_ensure_table_executes_create_sql():
    conn = _make_mock_conn()
    ensure_table(conn)

    cursor = conn.cursor.return_value.__enter__.return_value
    sql_called = cursor.execute.call_args[0][0]
    assert "CREATE TABLE IF NOT EXISTS termsheets" in sql_called


def test_insert_termsheet_returns_id():
    conn = _make_mock_conn(row_id=42)
    result = insert_termsheet(conn, SAMPLE_DATA)
    assert result == 42


def test_insert_termsheet_passes_correct_data():
    conn = _make_mock_conn(row_id=1)
    insert_termsheet(conn, SAMPLE_DATA)

    cursor = conn.cursor.return_value.__enter__.return_value
    _, kwargs_passed = cursor.execute.call_args
    # execute is called with positional args: (sql, params)
    params = cursor.execute.call_args[0][1]
    assert params["deal_name"] == "Project Apollo"
    assert params["borrower"] == "Apollo Industries Ltd."
    assert params["currency"] == "USD"
    assert params["raw_text"] == "raw termsheet text"


def test_get_connection_commits_on_success(monkeypatch):
    mock_conn = MagicMock()
    monkeypatch.setenv("POSTGRES_HOST", "localhost")
    monkeypatch.setenv("POSTGRES_DB", "testdb")
    monkeypatch.setenv("POSTGRES_USER", "user")
    monkeypatch.setenv("POSTGRES_PASSWORD", "pass")

    with patch("src.database.psycopg2.connect", return_value=mock_conn):
        with get_connection() as conn:
            assert conn is mock_conn

    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()


def test_get_connection_rolls_back_on_error(monkeypatch):
    mock_conn = MagicMock()
    monkeypatch.setenv("POSTGRES_HOST", "localhost")

    with patch("src.database.psycopg2.connect", return_value=mock_conn):
        with pytest.raises(ValueError):
            with get_connection() as conn:
                raise ValueError("test error")

    mock_conn.rollback.assert_called_once()
    mock_conn.close.assert_called_once()


def test_get_connection_uses_env_params(monkeypatch):
    monkeypatch.setenv("POSTGRES_HOST", "db.example.com")
    monkeypatch.setenv("POSTGRES_PORT", "5433")
    monkeypatch.setenv("POSTGRES_DB", "mydb")
    monkeypatch.setenv("POSTGRES_USER", "myuser")
    monkeypatch.setenv("POSTGRES_PASSWORD", "secret")

    mock_conn = MagicMock()
    with patch("src.database.psycopg2.connect", return_value=mock_conn) as mock_connect:
        with get_connection():
            pass

    mock_connect.assert_called_once_with(
        host="db.example.com",
        port=5433,
        dbname="mydb",
        user="myuser",
        password="secret",
    )
