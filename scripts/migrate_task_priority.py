"""One-time migration for adding task priorities to an existing database.

Run with the same DATABASE_URL as Fernward:
    python scripts/migrate_task_priority.py

Back up your database before running this on production.
"""
import os
from sqlalchemy import create_engine, inspect, text

url = os.environ.get("DATABASE_URL", "sqlite:///instance/secure_todo.db")
if url.startswith("postgres://"):
    url = "postgresql+psycopg://" + url[len("postgres://"):]
elif url.startswith("postgresql://"):
    url = "postgresql+psycopg://" + url[len("postgresql://"):]

engine = create_engine(url)
with engine.begin() as connection:
    inspector = inspect(connection)
    if "task" not in inspector.get_table_names():
        raise SystemExit("Task table does not exist; initialize the database first.")
    columns = {column["name"] for column in inspector.get_columns("task")}
    if "priority" not in columns:
        connection.execute(text(
            "ALTER TABLE task ADD COLUMN priority VARCHAR(16) NOT NULL DEFAULT 'medium'"
        ))
        print("Added task.priority; existing tasks default to medium.")
    else:
        connection.execute(text(
            "UPDATE task SET priority = 'medium' WHERE priority IS NULL OR priority = ''"
        ))
        print("Priority column already exists; filled missing priorities.")
print("Migration complete.")
