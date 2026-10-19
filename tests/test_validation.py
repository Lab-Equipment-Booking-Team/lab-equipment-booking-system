"""Unit and integration tests for Module M4 - Booking Validation & QA."""

import os
import sys
import types
from datetime import date, datetime, time

from flask_sqlalchemy import SQLAlchemy

# 1. Setup mock database module before importing app models
dummy_db_module = types.ModuleType("database")
dummy_database_submodule = types.ModuleType("database.database")
dummy_database_submodule.db = SQLAlchemy()
dummy_db_module.database = dummy_database_submodule

sys.modules["database"] = dummy_db_module
sys.modules["database.database"] = dummy_database_submodule

# 2. Add root path to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)



# 3. Validation rule checker (FR-03 Boundary & Rules)
def validate_booking_request(equipment_id, booking_date, start_time, end_time, quantity, purpose):
    if end_time <= start_time:
        return False, "End time must be after start time"
    
    start_dt = datetime.combine(date.today(), start_time)
    end_dt = datetime.combine(date.today(), end_time)
    duration_minutes = (end_dt - start_dt).total_seconds() / 60
    
    if duration_minutes < 30:
        return False, "Duration must be at least 30 minutes"
    if duration_minutes > 240:
        return False, "Duration cannot exceed 4 hours"
        
    return True, None

# 4. Unit Tests (Boundary Value Analysis for FR-03)
def test_end_time_before_start_time():
    start = time(10, 0)
    end = time(9, 30)
    is_valid, msg = validate_booking_request(1, date.today(), start, end, 1, "Test")
    assert is_valid is False
    assert msg == "End time must be after start time"

def test_duration_29_minutes():
    """Boundary Test: 29 minutes is below minimum (30 mins), so it must be REJECTED."""
    start = time(10, 0)
    end = time(10, 29)
    is_valid, msg = validate_booking_request(1, date.today(), start, end, 1, "Test")
    assert is_valid is False  # Corrected: Must be rejected!
    assert msg == "Duration must be at least 30 minutes"

def test_duration_30_minutes():
    """Boundary Test: Exactly 30 minutes is the minimum allowed, so it must be ACCEPTED."""
    start = time(10, 0)
    end = time(10, 30)
    is_valid, msg = validate_booking_request(1, date.today(), start, end, 1, "Test")
    assert is_valid is True
    assert msg is None

def test_duration_4_hours():
    """Boundary Test: Exactly 4 hours (240 mins) is the maximum allowed, ACCEPTED."""
    start = time(10, 0)
    end = time(14, 0)
    is_valid, msg = validate_booking_request(1, date.today(), start, end, 1, "Test")
    assert is_valid is True
    assert msg is None

def test_duration_over_4_hours():
    """Boundary Test: 4 hours and 1 minute exceeds maximum, REJECTED."""
    start = time(10, 0)
    end = time(14, 1)
    is_valid, msg = validate_booking_request(1, date.today(), start, end, 1, "Test")
    assert is_valid is False
    assert msg == "Duration cannot exceed 4 hours"