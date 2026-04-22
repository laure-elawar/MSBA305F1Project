import sqlite3
import pandas as pd
import os

def get_connection(db_path=':memory:'):
    """Return a sqlite3 connection. Use file path or ':memory:'."""
    conn = sqlite3.connect(db_path)
    return conn

def load_csv_to_sqlite(csv_path, conn=None, table_name='f1'):
    """Load a CSV into SQLite. If conn is None, create an in-memory DB and return it.

    Returns the connection object containing the table.
    """
    close_conn = False
    if conn is None:
        conn = get_connection(':memory:')
        close_conn = False

    df = pd.read_csv(csv_path)
    # Ensure column names are safe for SQL
    df.columns = [c.strip().replace(' ', '_') for c in df.columns]
    df.to_sql(table_name, conn, index=False, if_exists='replace')
    return conn
