"""Add task.priority without replacing users, tasks, or existing priorities.

Inspect first: python scripts/migrate_task_priority.py --check
Then migrate: python scripts/migrate_task_priority.py
Back up the database and stop application writers before a real migration.
"""
import argparse
from pathlib import Path
import sys

# Direct invocation works from any directory without importing app.py,
# requiring authentication secrets, or initializing Redis/session services.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text
from database_config import PROJECT_ROOT, get_database_uri, load_environment


def create_migration_app():
    load_environment()
    # Match Flask's import name/root and let Flask-SQLAlchemy resolve SQLite
    # paths under the instance directory, just as it does for app.py.
    app = Flask('app', root_path=str(PROJECT_ROOT),
                instance_path=str(PROJECT_ROOT / 'instance'))
    app.config['SQLALCHEMY_DATABASE_URI'] = get_database_uri()
    db = SQLAlchemy(app)
    return app, db


def priority_columns(connection):
    inspector = inspect(connection)
    if 'task' not in inspector.get_table_names():
        raise ValueError('Task table does not exist; initialize the database first.')
    return {column['name'] for column in inspector.get_columns('task')}


def migrate(connection):
    columns = priority_columns(connection)
    if 'priority' not in columns:
        connection.execute(text(
            "ALTER TABLE task ADD COLUMN priority VARCHAR(16) NOT NULL DEFAULT 'medium'"
        ))
        return 'Added task.priority; existing tasks default to medium.'
    result = connection.execute(text(
        "UPDATE task SET priority = 'medium' WHERE priority IS NULL OR priority = ''"
    ))
    return f'Priority column already exists; filled {result.rowcount} missing priorities.'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Report schema status without changing data.')
    args = parser.parse_args(argv)
    app, db = create_migration_app()
    try:
        with app.app_context():
            engine = db.engine
            if engine.dialect.name == 'sqlite':
                filename = engine.url.database
                if not filename or filename == ':memory:':
                    raise ValueError('A migration requires an existing on-disk SQLite database.')
                if engine.url.query.get('uri'):
                    raise ValueError('SQLite URI filenames are not supported by this maintenance command; use a regular SQLite DATABASE_URL for the same file.')
                path = Path(filename).resolve()
                print(f'SQLite database: {path}')
                # SQLite must not silently create a database at a wrong path.
                if not path.is_file():
                    raise ValueError('Database file does not exist; no database was created or migrated.')
            else:
                # Never print database credentials or the connection URL.
                print(f'Database backend: {engine.dialect.name}')
            if args.check:
                with engine.connect() as connection:
                    if 'priority' not in priority_columns(connection):
                        print('Migration required: task.priority is missing.')
                        return 1
                    missing = connection.execute(text(
                        "SELECT COUNT(*) FROM task WHERE priority IS NULL OR priority = ''"
                    )).scalar_one()
                    if missing:
                        print(f'Migration required: {missing} tasks have missing priorities.')
                        return 1
                    print('Task priority schema is ready; no changes made.')
                    return 0
            with engine.begin() as connection:
                print(migrate(connection))
            print('Migration complete.')
            return 0
    finally:
        with app.app_context():
            db.engine.dispose()


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except ValueError as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(2)
