# Task priority migration

The Task model includes priority, but SQLAlchemy create_all() does not add columns to an existing table. An older task table therefore fails when the dashboard selects task.priority.

The previous standalone migration skipped dotenv loading and resolved SQLite paths with plain SQLAlchemy relative to the shell's working directory. Flask loaded dotenv and Flask-SQLAlchemy resolved relative SQLite paths under its instance directory. A migration could therefore inspect a different file.

## Configuration and path

Flask and the migration now share database_config.py: the project .env is loaded without overriding exported environment variables, DATABASE_URL defaults to sqlite:///secure_todo.db, and legacy PostgreSQL schemes retain the contributor's psycopg normalization. The migration uses Flask-SQLAlchemy's SQLite resolution rather than hand-building a filesystem path.

- Default URL: <project>/instance/secure_todo.db.
- sqlite:///custom.db: <project>/instance/custom.db (not the current directory).
- Absolute SQLite URL: the explicitly named file.
- DATABASE_URL exported by the shell takes precedence over the project's .env.

No database is opened merely by importing the migration module. The command does not import app.py or require authentication secrets/Redis. It prints only the SQLite filename or backend name, never connection credentials. Missing database files are rejected before connecting. SQLite URI filenames (uri=true) are refused explicitly; use an ordinary SQLite URL pointing to the same file for this maintenance command.

## Manual step on the real application

No existing application database or .env was modified during this fix. Run these commands in the application's existing virtual environment, with the same environment as Flask, from the project directory:

    python scripts/migrate_task_priority.py --check

Verify the reported filename is the database used by your Flask process. Check exit codes: 0 means ready, 1 means migration required, and 2 means a missing file/table or unsupported SQLite target. In-memory databases cannot be migrated by this standalone command.

If migration is required, stop application writers and make a consistent backup of that reported database first. Then run:

    python scripts/migrate_task_priority.py
    python scripts/migrate_task_priority.py --check

Restart Flask and open the dashboard. Do not use create_all(), delete the database, or recreate tables as a substitute for this migration.

The migration adds a non-null priority column with a server default of medium. Existing tasks receive medium. Reruns do not add another column or change valid priorities; a partially migrated nullable column has only NULL/empty priorities backfilled. User records, task IDs, ownership, titles, completion states, timestamps, and valid existing priorities remain intact. The script does not rebuild tables or reset data.

## Verification

18 Python tests pass (11 task-route tests and 7 migration/configuration tests). Tests copy code into temporary projects and use synthetic .env files and disposable SQLite databases. Coverage includes exact dashboard error reproduction, successful loading afterward, default/relative/absolute path matching with Flask from another directory, dotenv/exported-variable precedence, read-only check behavior, missing-file/table refusal, repeated migration, original-copy hash preservation, retained user/task fields, server defaults, partial backfill, low/medium/high priorities, normalization, missing/default and invalid priorities, JSON/form creation, completion/reversal, deletion confirmation, CSRF, and ownership.

The prior dashboard test incorrectly prohibited every select element; it now permits the implemented priority selector while still excluding the unfinished toolbar. Initial new migration tests exposed Windows file-handle cleanup errors; their temporary SQLite connections now close explicitly. The final suite has no failures. Existing Node focus regressions and whitespace checks are also run separately.

No tests were run against production data or live Redis/PostgreSQL/Turnstile. The real database still needs the manual check/migration above. Changes are intentionally uncommitted and unpushed on fix/priorities-review.
