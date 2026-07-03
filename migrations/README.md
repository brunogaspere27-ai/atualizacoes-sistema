Simple migrations runner

Usage:

1. Place SQL files in this folder named with a leading sequence number, e.g. `001_create_sync_log.sql`.
2. Run the runner to apply pending migrations:

```bash
python migrations/apply_migrations.py
```

The runner records applied migrations in `migrations_applied` table inside the SQLite database.
