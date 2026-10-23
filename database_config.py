"""Database environment shared by Flask and maintenance commands."""
import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent


def load_environment():
    # Exported variables retain precedence over the project .env file.
    load_dotenv(PROJECT_ROOT / '.env', override=False)


def get_database_uri():
    url = os.environ.get('DATABASE_URL', 'sqlite:///secure_todo.db')
    if url.startswith('postgres://'):
        return 'postgresql+psycopg://' + url[len('postgres://'):]
    if url.startswith('postgresql://'):
        return 'postgresql+psycopg://' + url[len('postgresql://'):]
    return url
