import os
import sqlite3
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH", os.path.join("data", "aster_database.db"))
DB_URL = os.getenv("DB_URL")

def migrate():
    sqlite_conn = sqlite3.connect(DB_PATH)
    pg_engine = create_engine(DB_URL)

    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT name from sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row[0] for row in cursor.fetchall()]
    for table in tables:
        df = pd.read_sql_query(f'SELECT * FROM "{table}"', sqlite_conn)
        df.to_sql(table, pg_engine, if_exists="replace", index=False)

    sqlite_conn.close()

if __name__ == "__main__":
    migrate()