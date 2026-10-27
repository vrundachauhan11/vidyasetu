"""VidyaSetu - Database Migration Script (SQLite -> PostgreSQL).
Copies all tables and data from local SQLite (vidyasetu.db) into a target PostgreSQL database.
Preserves primary keys, foreign keys, timestamps, and cryptographic audit tamper hashes.
"""
import os
import sys
import sqlite3
import argparse
from sqlalchemy import create_engine, MetaData, Table, select
from sqlalchemy.orm import sessionmaker

def migrate(sqlite_path: str, pg_url: str):
    if not os.path.exists(sqlite_path):
        print(f"Error: SQLite source file {sqlite_path} not found.")
        sys.exit(1)

    print(f"--- VIDYASETU DATABASE MIGRATION ---")
    print(f"Source SQLite:     {sqlite_path}")
    print(f"Target PostgreSQL: {pg_url.split('@')[-1] if '@' in pg_url else 'PostgreSQL'}")

    # Synchronous URL for migration
    sync_pg_url = pg_url.replace("+asyncpg", "")
    pg_engine = create_engine(sync_pg_url)
    
    # Connect to SQLite
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()

    tables = [
        "institutions",
        "programme_approvals",
        "intake_batches",
        "student_enrolments",
        "integrity_signals",
        "audit_logs",
    ]

    with pg_engine.begin() as pg_conn:
        meta = MetaData()
        meta.reflect(bind=pg_engine)

        for table_name in tables:
            if table_name not in meta.tables:
                print(f"Warning: Table {table_name} does not exist in target PostgreSQL. Run migrations first.")
                continue

            pg_table = meta.tables[table_name]
            sqlite_cursor.execute(f"SELECT * FROM {table_name}")
            rows = [dict(r) for r in sqlite_cursor.fetchall()]
            
            if rows:
                print(f"Migrating {len(rows):<4} rows into {table_name}...")
                # Clear existing to avoid duplicate key errors
                pg_conn.execute(pg_table.delete())
                pg_conn.execute(pg_table.insert(), rows)
            else:
                print(f"Table {table_name} is empty; skipping.")

    sqlite_conn.close()
    print("Migration completed successfully!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate VidyaSetu SQLite to PostgreSQL")
    parser.add_argument("--sqlite", default="vidyasetu.db", help="Path to SQLite file")
    parser.add_argument("--postgres", required=True, help="PostgreSQL connection string")
    args = parser.parse_args()

    migrate(args.sqlite, args.postgres)
