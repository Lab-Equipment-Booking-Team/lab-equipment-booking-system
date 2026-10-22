"""Backward-compatibility proxy for Lab Equipment Booking System models.

The canonical database models and ORM entities are managed under:
modules/M3_booking_form_model/models.py
and database/database.py.
"""

from database.database import db, utcnow
from modules.M3_booking_form_model.models import Booking, Equipment, User

__all__ = ["Booking", "Equipment", "User", "db", "utcnow"]
