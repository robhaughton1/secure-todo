"""Initialize Fernward database tables before the first deployment.

This is suitable for initial setup, not schema migrations after data exists.
"""
from app import application, database

with application.app_context():
    database.create_all()
    print("Database tables initialized.")
