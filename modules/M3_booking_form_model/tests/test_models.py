from datetime import date, time

from database.database import db
from modules.M3_booking_form_model.models import Booking, Equipment, User


def test_user_model_operations(app):
    """Test User model creation, password hashing, and role checks."""
    user = User(
        username="test_model_user",
        email="test_model@university.edu",
        full_name="Model User",
        student_or_staff_id="STU-MODEL-01",
        role=User.ROLE_STUDENT,
    )
    user.set_password("MySecretPass123!")
    db.session.add(user)
    db.session.commit()

    saved_user = User.query.filter_by(username="test_model_user").first()
    assert saved_user is not None
    assert saved_user.id is not None
    assert saved_user.check_password("MySecretPass123!") is True
    assert saved_user.check_password("WrongPass") is False
    assert saved_user.is_student_member is True
    assert saved_user.is_staff_member is False
    assert "test_model_user" in repr(saved_user)


def test_equipment_model_operations(app):
    """Test Equipment model attributes, statuses, and deletion eligibility."""
    eq = Equipment(
        code="EQ-MODEL-01",
        name="Model Optical Bench",
        category="Spectrometry & Optical",
        description="High precision optical bench",
        quantity_available=4,
        status=Equipment.STATUS_AVAILABLE,
    )
    db.session.add(eq)
    db.session.commit()

    assert eq.id is not None
    assert eq.is_operational is True
    assert eq.can_be_deleted() is True
    assert "EQ-MODEL-01" in repr(eq)


def test_booking_model_and_relationships(app, student_user, sample_equipment, staff_user):
    """Test Booking model relationships with User and Equipment."""
    booking = Booking(
        user_id=student_user.id,
        equipment_id=sample_equipment.id,
        booking_date=date(2026, 11, 20),
        start_time=time(13, 0),
        end_time=time(15, 0),
        quantity=1,
        purpose="Relationship verification experiment",
        status=Booking.STATUS_PENDING,
    )
    db.session.add(booking)
    db.session.commit()

    # Relationship traversal
    assert booking.user.id == student_user.id
    assert booking.equipment.id == sample_equipment.id
    assert booking in student_user.bookings
    assert booking in sample_equipment.bookings

    # Equipment now cannot be deleted
    assert sample_equipment.can_be_deleted() is False

    # Status check
    assert booking.is_pending is True
    assert booking.is_approved is False

    # Staff approval
    booking.approve(staff_user)
    db.session.commit()

    assert booking.is_approved is True
    assert booking.reviewed_by_id == staff_user.id
    assert booking in staff_user.reviewed_bookings
    assert booking.reviewer.username == staff_user.username
