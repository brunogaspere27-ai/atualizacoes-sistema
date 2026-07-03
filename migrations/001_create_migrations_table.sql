-- Initial migration placeholder
CREATE TABLE IF NOT EXISTS migrations_applied (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT UNIQUE,
    applied_at TEXT DEFAULT CURRENT_TIMESTAMP
);
