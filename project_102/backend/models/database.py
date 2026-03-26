"""
Database configuration and initialization
DMMMSU-SLUC Disaster/Emergency Incident Report Monitoring System

Supports MySQL (via PyMySQL) with SQLite fallback for local dev.
Connection parameters are read from environment variables / .env file.
"""

import os

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def get_database_uri() -> str:
    """Build the SQLAlchemy database URI from environment variables."""
    db_host = os.environ.get("DB_HOST", "127.0.0.1")
    db_port = os.environ.get("DB_PORT", "3307")
    db_user = os.environ.get("DB_USER", "root")
    db_pass = os.environ.get("DB_PASSWORD", "")
    db_name = os.environ.get("DB_NAME", "campus_incidents_db")

    # If DATABASE_URL is explicitly set (e.g. on a cloud host), use it directly
    explicit_url = os.environ.get("DATABASE_URL")
    if explicit_url:
        return explicit_url

    # Build MySQL + PyMySQL URI
    return (
        f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}"
        f"/{db_name}?charset=utf8mb4"
    )


def init_db():
    """Initialize database tables (create any that are missing)."""
    db.create_all()
