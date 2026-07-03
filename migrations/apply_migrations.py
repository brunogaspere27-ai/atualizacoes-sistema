import sqlite3
import os
from pathlib import Path

from config.settings import settings

MIGRATIONS_DIR = Path(__file__).parent
DB_PATH = settings.db_path


def ensure_table(conn: sqlite3.Connection):
    conn.execute("""
    CREATE TABLE IF NOT EXISTS migrations_applied (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT UNIQUE,
        applied_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)


def applied(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("SELECT filename FROM migrations_applied")
    return {row[0] for row in cur.fetchall()}


def apply_migration(conn: sqlite3.Connection, filename: Path):
    sql = filename.read_text(encoding="utf-8")
    conn.executescript(sql)
    conn.execute("INSERT INTO migrations_applied (filename) VALUES (?)", (filename.name,))


def main():
    if not DB_PATH.exists():
        print("Database not found. Ensure the application created the DB before running migrations.")
        return

    conn = sqlite3.connect(str(DB_PATH))
    ensure_table(conn)
    applied_set = applied(conn)

    files = sorted([p for p in MIGRATIONS_DIR.iterdir() if p.suffix == ".sql"])
    pending = [f for f in files if f.name not in applied_set]

    if not pending:
        print("No pending migrations.")
        return

    for f in pending:
        print(f"Applying {f.name}...")
        apply_migration(conn, f)
        conn.commit()
        print(f"Applied {f.name}")

    conn.close()
    print("Migrations complete.")


if __name__ == "__main__":
    main()
