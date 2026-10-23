from datetime import date, time, timedelta

from database.database import db
from modules.M3_booking_form_model.models import Booking
from tests.conftest import login_client


def test_student_submit_valid_booking_request(client, student_user, sample_equipment):
    """Test student successfully submitting a valid booking request."""
    login_client(client, student_user.username, "StudentSecret123!")

    future_date = date.today() + timedelta(days=5)

    response = client.post(
        "/student/book",
        data={
            "equipment_id": sample_equipment.id,
            "booking_date": future_date.strftime("%Y-%m-%d"),
            "start_time": "10:00",
            "end_time": "12:00",
            "quantity": 1,
            "purpose": "Molecular genetics experiment for Bio 301",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"submitted successfully" in response.data
    assert b"Pending Staff Review" in response.data

    booking = Booking.query.filter_by(user_id=student_user.id).first()
    assert booking is not None
    assert booking.equipment_id == sample_equipment.id
    assert booking.status == Booking.STATUS_PENDING
    assert booking.quantity == 1
    assert booking.purpose == "Molecular genetics experiment for Bio 301"


def test_reject_past_booking_date(client, student_user, sample_equipment):
    """Test that booking dates in the past are persisted as Rejected with a reason."""
    login_client(client, student_user.username, "StudentSecret123!")

    past_date = date.today() - timedelta(days=2)

    response = client.post(
        "/student/book",
        data={
            "equipment_id": sample_equipment.id,
            "booking_date": past_date.strftime("%Y-%m-%d"),
            "start_time": "10:00",
            "end_time": "12:00",
            "quantity": 1,
            "purpose": "Attempting past date booking",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"cannot be in the past" in response.data

    # Booking is now persisted as Rejected (not silently dropped).
    booking = Booking.query.filter_by(user_id=student_user.id).first()
    assert booking is not None
    assert booking.status == Booking.STATUS_REJECTED
    assert booking.rejection_reason is not None
    assert "past" in booking.rejection_reason.lower()


def test_reject_start_time_after_or_equal_end_time(client, student_user, sample_equipment):
    """Test that start time >= end time is rejected."""
    login_client(client, student_user.username, "StudentSecret123!")

    future_date = date.today() + timedelta(days=3)

    # Start time equal to end time
    resp_equal = client.post(
        "/student/book",
        data={
            "equipment_id": sample_equipment.id,
            "booking_date": future_date.strftime("%Y-%m-%d"),
            "start_time": "11:00",
            "end_time": "11:00",
            "quantity": 1,
            "purpose": "Equal start and end time test",
        },
        follow_redirects=True,
    )
    assert b"must be strictly earlier than the end time" in resp_equal.data

    # Start time later than end time
    resp_inverted = client.post(
        "/student/book",
        data={
            "equipment_id": sample_equipment.id,
            "booking_date": future_date.strftime("%Y-%m-%d"),
            "start_time": "14:00",
            "end_time": "10:00",
            "quantity": 1,
            "purpose": "Inverted time test",
        },
        follow_redirects=True,
    )
    assert b"must be strictly earlier than the end time" in resp_inverted.data

    # Both invalid submissions are persisted as Rejected records.
    rejected = Booking.query.filter_by(status=Booking.STATUS_REJECTED).all()
    assert len(rejected) == 2
    assert all(b.rejection_reason is not None for b in rejected)


def test_reject_booking_on_maintenance_equipment(client, student_user, maintenance_equipment):
    """Test that equipment under maintenance cannot be booked."""
    login_client(client, student_user.username, "StudentSecret123!")

    future_date = date.today() + timedelta(days=4)

    response = client.post(
        "/student/book",
        data={
            "equipment_id": maintenance_equipment.id,
            "booking_date": future_date.strftime("%Y-%m-%d"),
            "start_time": "09:00",
            "end_time": "11:00",
            "quantity": 1,
            "purpose": "Attempting to book broken centrifuge",
        },
        follow_redirects=True,
    )
    assert b"currently under maintenance and cannot be booked" in response.data

    # Booking is persisted as Rejected — equipment FK is valid even under maintenance.
    booking = Booking.query.filter_by(user_id=student_user.id).first()
    assert booking is not None
    assert booking.status == Booking.STATUS_REJECTED
    assert booking.rejection_reason is not None
    assert "maintenance" in booking.rejection_reason.lower()


def test_reject_invalid_quantity(client, student_user, sample_equipment):
    """Test that zero, negative, or excess quantities are rejected."""
    login_client(client, student_user.username, "StudentSecret123!")
    future_date = date.today() + timedelta(days=2)

    # Zero quantity
    resp1 = client.post(
        "/student/book",
        data={
            "equipment_id": sample_equipment.id,
            "booking_date": future_date.strftime("%Y-%m-%d"),
            "start_time": "09:00",
            "end_time": "11:00",
            "quantity": 0,
            "purpose": "Zero quantity test",
        },
        follow_redirects=True,
    )
    assert b"positive integer" in resp1.data

    # Exceeding inventory count (sample_equipment has 3 units)
    resp2 = client.post(
        "/student/book",
        data={
            "equipment_id": sample_equipment.id,
            "booking_date": future_date.strftime("%Y-%m-%d"),
            "start_time": "09:00",
            "end_time": "11:00",
            "quantity": 10,
            "purpose": "Exceeding quantity test",
        },
        follow_redirects=True,
    )
    assert b"exceeds total equipment inventory" in resp2.data


def test_student_cancel_pending_booking(client, student_user, sample_equipment):
    """Test student cancelling their own pending booking request."""
    future_date = date.today() + timedelta(days=3)
    booking = Booking(
        user_id=student_user.id,
        equipment_id=sample_equipment.id,
        booking_date=future_date,
        start_time=time(10, 0),
        end_time=time(12, 0),
        quantity=1,
        purpose="Cancel test",
        status=Booking.STATUS_PENDING,
    )
    db.session.add(booking)
    db.session.commit()
    b_id = booking.id

    login_client(client, student_user.username, "StudentSecret123!")
    response = client.post(f"/student/bookings/{b_id}/cancel", follow_redirects=True)
    assert response.status_code == 200
    assert b"has been cancelled" in response.data

    db.session.refresh(booking)
    assert booking.status == Booking.STATUS_CANCELLED


def test_student_cannot_cancel_approved_booking(client, student_user, sample_equipment):
    """Ensure student cannot cancel a booking that has already been approved."""
    future_date = date.today() + timedelta(days=3)
    booking = Booking(
        user_id=student_user.id,
        equipment_id=sample_equipment.id,
        booking_date=future_date,
        start_time=time(10, 0),
        end_time=time(12, 0),
        quantity=1,
        purpose="Cannot cancel approved test",
        status=Booking.STATUS_APPROVED,
    )
    db.session.add(booking)
    db.session.commit()

    login_client(client, student_user.username, "StudentSecret123!")
    response = client.post(f"/student/bookings/{booking.id}/cancel", follow_redirects=True)
    assert b"Cannot cancel booking" in response.data

    db.session.refresh(booking)
    assert booking.status == Booking.STATUS_APPROVED


# ---------------------------------------------------------------------------
# Auto-rejection persistence tests (new behaviour)
# ---------------------------------------------------------------------------


def test_auto_reject_persists_rejected_record_for_past_date(
    app, student_user, sample_equipment
):
    """Directly test create_student_booking: past date → Rejected record in DB."""
    from modules.M3_booking_form_model.service import create_student_booking

    past_date = date.today() - timedelta(days=1)

    with app.app_context():
        booking, error = create_student_booking(
            user_id=student_user.id,
            equipment_id=sample_equipment.id,
            date_str=past_date.strftime("%Y-%m-%d"),
            start_time_str="10:00",
            end_time_str="12:00",
            quantity=1,
            purpose="Service-level past date test",
        )
        # Assertions must be inside the context so the session is still active.
        assert error is not None, "Expected an error message for past date"
        assert booking is not None, "Expected a persisted Rejected booking record"
        assert booking.id is not None
        assert booking.status == Booking.STATUS_REJECTED
        assert booking.rejection_reason is not None
        assert booking.reviewed_by_id is None  # System rejection — no staff reviewer



def test_auto_reject_booking_model_method(sample_equipment, student_user):
    """Unit test: Booking.auto_reject() sets status, reason, and leaves reviewer None."""
    from datetime import date as _date
    from datetime import time as _time

    b = Booking(
        user_id=student_user.id,
        equipment_id=sample_equipment.id,
        booking_date=_date.today(),
        start_time=_time(9, 0),
        end_time=_time(11, 0),
        quantity=1,
        purpose="Unit test for auto_reject",
        status=Booking.STATUS_PENDING,
    )
    b.auto_reject("Time slot conflict with an existing approved booking.")

    assert b.status == Booking.STATUS_REJECTED
    assert "conflict" in b.rejection_reason.lower()
    assert b.reviewed_by_id is None
    assert b.reviewed_at is None
