from datetime import date, time, timedelta

from models import Booking, db
from tests.conftest import login_client


def test_staff_approve_booking_request(client, staff_user, student_user, sample_equipment):
    """Test staff successfully approving a pending booking request."""
    future_date = date.today() + timedelta(days=5)
    booking = Booking(
        user_id=student_user.id,
        equipment_id=sample_equipment.id,
        booking_date=future_date,
        start_time=time(10, 0),
        end_time=time(12, 0),
        quantity=1,
        purpose="Staff approval test",
        status=Booking.STATUS_PENDING,
    )
    db.session.add(booking)
    db.session.commit()
    b_id = booking.id

    login_client(client, staff_user.username, "StaffSecret123!")
    response = client.post(
        f"/staff/requests/{b_id}/approve",
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"has been Approved" in response.data

    db.session.refresh(booking)
    assert booking.status == Booking.STATUS_APPROVED
    assert booking.reviewed_by_id == staff_user.id
    assert booking.reviewed_at is not None
    assert booking.rejection_reason is None


def test_staff_reject_booking_request_with_reason(
    client, staff_user, student_user, sample_equipment
):
    """Test staff rejecting a pending request with a constructive reason."""
    future_date = date.today() + timedelta(days=5)
    booking = Booking(
        user_id=student_user.id,
        equipment_id=sample_equipment.id,
        booking_date=future_date,
        start_time=time(10, 0),
        end_time=time(12, 0),
        quantity=1,
        purpose="Staff rejection test",
        status=Booking.STATUS_PENDING,
    )
    db.session.add(booking)
    db.session.commit()
    b_id = booking.id

    login_client(client, staff_user.username, "StaffSecret123!")
    response = client.post(
        f"/staff/requests/{b_id}/reject",
        data={"rejection_reason": "Lab undergoes annual calibration on that date."},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"has been Rejected" in response.data

    db.session.refresh(booking)
    assert booking.status == Booking.STATUS_REJECTED
    assert booking.reviewed_by_id == staff_user.id
    assert booking.rejection_reason == "Lab undergoes annual calibration on that date."


def test_prevent_invalid_status_transitions(
    client, staff_user, student_user, sample_equipment
):
    """Test preventing double-approval or approval of an already rejected request."""
    future_date = date.today() + timedelta(days=5)
    booking = Booking(
        user_id=student_user.id,
        equipment_id=sample_equipment.id,
        booking_date=future_date,
        start_time=time(10, 0),
        end_time=time(12, 0),
        quantity=1,
        purpose="State transition test",
        status=Booking.STATUS_REJECTED,
    )
    db.session.add(booking)
    db.session.commit()
    b_id = booking.id

    login_client(client, staff_user.username, "StaffSecret123!")

    # Attempting to re-approve a rejected request
    resp = client.post(f"/staff/requests/{b_id}/approve", follow_redirects=True)
    assert b"Invalid transition" in resp.data

    # Attempting to reject an already rejected request
    resp2 = client.post(f"/staff/requests/{b_id}/reject", follow_redirects=True)
    assert b"Invalid transition" in resp2.data


def test_reapproval_capacity_conflict_prevention(
    client, staff_user, student_user, student_user_two, single_unit_equipment
):
    """Test that if two pending requests compete for 1 unit, approving the second fails with capacity conflict."""
    test_date = date.today() + timedelta(days=4)

    # First pending request
    b1 = Booking(
        user_id=student_user.id,
        equipment_id=single_unit_equipment.id,
        booking_date=test_date,
        start_time=time(10, 0),
        end_time=time(12, 0),
        quantity=1,
        purpose="Request 1",
        status=Booking.STATUS_PENDING,
    )
    # Second competing pending request for same slot
    b2 = Booking(
        user_id=student_user_two.id,
        equipment_id=single_unit_equipment.id,
        booking_date=test_date,
        start_time=time(10, 0),
        end_time=time(12, 0),
        quantity=1,
        purpose="Request 2",
        status=Booking.STATUS_PENDING,
    )
    db.session.add_all([b1, b2])
    db.session.commit()

    login_client(client, staff_user.username, "StaffSecret123!")

    # Approve request 1 -> should succeed
    resp1 = client.post(f"/staff/requests/{b1.id}/approve", follow_redirects=True)
    assert b"has been Approved" in resp1.data

    # Attempt to approve request 2 -> should be blocked due to capacity conflict!
    resp2 = client.post(f"/staff/requests/{b2.id}/approve", follow_redirects=True)
    assert b"Cannot approve" in resp2.data
    assert b"Capacity conflict" in resp2.data

    db.session.refresh(b2)
    assert b2.status == Booking.STATUS_PENDING  # Remains pending


def test_student_forbidden_from_approving_or_rejecting(
    client, student_user, sample_equipment
):
    """Test that student accounts are strictly forbidden from approving or rejecting requests."""
    future_date = date.today() + timedelta(days=5)
    booking = Booking(
        user_id=student_user.id,
        equipment_id=sample_equipment.id,
        booking_date=future_date,
        start_time=time(10, 0),
        end_time=time(12, 0),
        quantity=1,
        purpose="Unauthorized action test",
        status=Booking.STATUS_PENDING,
    )
    db.session.add(booking)
    db.session.commit()
    b_id = booking.id

    login_client(client, student_user.username, "StudentSecret123!")

    # Student attempts approve
    resp1 = client.post(f"/staff/requests/{b_id}/approve")
    assert resp1.status_code == 403

    # Student attempts reject
    resp2 = client.post(f"/staff/requests/{b_id}/reject")
    assert resp2.status_code == 403
