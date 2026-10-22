"""Shared database configuration and SQLAlchemy instance for Lab Equipment Booking System.

This central database module manages the shared SQLAlchemy session and lifecycle
across all five assigned project modules (M1 - M5).
"""

from datetime import UTC, datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Central SQLAlchemy instance shared by all modules
db = SQLAlchemy()


def utcnow() -> datetime:
    """Return timezone-naive UTC datetime for consistent database timestamps."""
    return datetime.now(UTC).replace(tzinfo=None)


def init_db(app: Flask) -> None:
    """Initialize database extension with the Flask application context."""
    db.init_app(app)
