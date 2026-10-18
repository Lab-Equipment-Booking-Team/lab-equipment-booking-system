"""Unit and integration tests for Module M4 – Booking Validation & QA.

Assigned to: Hashini Wickramasinghe (Student ID: 6317, GitHub: Hashini-123)
"""

from datetime import date, datetime, time, timedelta

from database.database import db
from modules.M3_booking_form_model.models import Booking
from modules.M4_booking_validation.validation import validate_booking_request


def test_no_conflict_on_different_dates(app, sample_equipment, student_user):
    """Test that bookings on different dates do not conflict."""
    date1 = date.today() + timedelta(days=5)
    date2 = date.today() + timedelta(days=6)

    # Approved booking on date1
    b1 = Booking(
        user_id=student_user.id,
        equipment_id=sample_equipment.id,
        booking_date=date1,
        start_time=time(10, 0),
        end_time=time(12, 0),
        quantity=3,  # Uses all units
        purpose="Experiment Day 1",
        status=Booking.STATUS_APPROVED,
    )
    db.session.add(b1)
    db.session.commit()

    # Request on date2 for same time should succeed
    is_valid, msg = validate_booking_request(
        equipment=sample_equipment,
        booking_date=date2,
        start_time=time(10, 0),
        end_time=time(12, 0),
        quantity=3,
        purpose="Experiment Day 2",
    )
    assert is_valid is True
    assert msg is None


def test_no_conflict_on_non_overlapping_times_same_date(
    app, sample_equipment, student_user
):
    """Ensure that distinct or adjacent time slots on the same date do not conflict."""
    test_date = date.today() + timedelta(days=5)

    # Approved booking from 09:00 to 11:00
    b1 = Booking(
        user_id=student_user.id,
        equipment_id=sample_equipment.id,
        booking_date=test_date,
        start_time=time(9, 0),
        end_time=time(11, 0),
        quantity=sample_equipment.quantity_available,  # Max out capacity
        purpose="Morning slot",
        status=Booking.STATUS_APPROVED,
    )
    db.session.add(b1)
    db.session.commit()

    # 1. Adjacent slot immediately following (11:00 to 13:00)
    is_valid_adj, msg_adj = validate_booking_request(
        equipment=sample_equipment,
        booking_date=test_date,
        start_time=time(11, 0),
        end_time=time(13, 0),
        quantity=sample_equipment.quantity_available,
        purpose="Adjacent slot",
    )
    assert is_valid_adj is True
    assert msg_adj is None

    # 2. Later afternoon slot (14:00 to 16:00)
    is_valid_aft, msg_aft = validate_booking_request(
        equipment=sample_equipment,
        booking_date=test_date,
        start_time=time(14, 0),
        end_time=time(16, 0),
        quantity=sample_equipment.quantity_available,
        purpose="Afternoon slot",
    )
    assert is_valid_aft is True
    assert msg_aft is None

    # 3. Earlier morning slot (07:00 to 09:00)
    is_valid_earl, msg_earl = validate_booking_request(
        equipment=sample_equipment,
        booking_date=test_date,
        start_time=time(7, 0),
        end_time=time(9, 0),
        quantity=sample_equipment.quantity_available,
        purpose="Early morning slot",
    )
    assert is_valid_earl is True
    assert msg_earl is None


def test_overlap_conflict_on_single_unit_equipment(
    app, single_unit_equipment, student_user
):
    """Test overlapping conflict on a single-unit resource."""
    test_date = date.today() + timedelta(days=4)

    # Approved booking 10:00 to 12:00
    b_appr = Booking(
        user_id=student_user.id,
        equipment_id=single_unit_equipment.id,
        booking_date=test_date,
        start_time=time(10, 0),
        end_time=time(12, 0),
        quantity=1,
        purpose="Approved single unit session",
        status=Booking.STATUS_APPROVED,
    )
    db.session.add(b_appr)
    db.session.commit()

    # 1. Partial overlap (11:00 to 13:00) -> must fail
    val1, err1 = validate_booking_request(
        equipment=single_unit_equipment,
        booking_date=test_date,
        start_time=time(11, 0),
        end_time=time(13, 0),
        quantity=1,
        purpose="Partial overlap test",
    )
    assert val1 is False
    assert "Capacity conflict" in err1

    # 2. Complete enclosing overlap (09:00 to 13:00) -> must fail
    val2, err2 = validate_booking_request(
        equipment=single_unit_equipment,
        booking_date=test_date,
        start_time=time(9, 0),
        end_time=time(13, 0),
        quantity=1,
        purpose="Enclosing overlap test",
    )
    assert val2 is False
    assert "Capacity conflict" in err2

    # 3. Inside overlap (10:30 to 11:30) -> must fail
    val3, err3 = validate_booking_request(
        equipment=single_unit_equipment,
        booking_date=test_date,
        start_time=time(10, 30),
        end_time=time(11, 30),
        quantity=1,
        purpose="Inside overlap test",
    )
    assert val3 is False
    assert "Capacity conflict" in err3


def test_multi_unit_partial_capacity_allocation(
    app, sample_equipment, student_user
):
    """Test multi-unit equipment (total = 3) allows non-exceeding concurrent bookings."""
    test_date = date.today() + timedelta(days=5)

    # Approved booking for 2 units from 10:00 to 12:00
    b1 = Booking(
        user_id=student_user.id,
        equipment_id=sample_equipment.id,
        booking_date=test_date,
        start_time=time(10, 0),
        end_time=time(12, 0),
        quantity=2,  # 2 of 3 booked
        purpose="Group project part 1",
        status=Booking.STATUS_APPROVED,
    )
    db.session.add(b1)
    db.session.commit()

    # Request for 1 unit during same time window -> passes! (2 + 1 = 3 <= 3)
    val_pass, err_pass = validate_booking_request(
        equipment=sample_equipment,
        booking_date=test_date,
        start_time=time(10, 0),
        end_time=time(12, 0),
        quantity=1,
        purpose="Single unit request during slot",
    )
    assert val_pass is True
    assert err_pass is None

    # Request for 2 units during same time window -> fails! (2 + 2 = 4 > 3)
    val_fail, err_fail = validate_booking_request(
        equipment=sample_equipment,
        booking_date=test_date,
        start_time=time(10, 0),
        end_time=time(12, 0),
        quantity=2,
        purpose="Exceeding request during slot",
    )
    assert val_fail is False
    assert "Capacity conflict" in err_fail
    assert "only 1 unit(s) remain available out of 3" in err_fail


def test_pending_and_rejected_bookings_do_not_block_capacity(
    app, sample_equipment, student_user
):
    """Ensure that only APPROVED bookings reserve inventory."""
    test_date = date.today() + timedelta(days=6)

    # 1. Pending booking using 3 units
    b_pending = Booking(
        user_id=student_user.id,
        equipment_id=sample_equipment.id,
        booking_date=test_date,
        start_time=time(10, 0),
        end_time=time(12, 0),
        quantity=3,
        purpose="Pending booking",
        status=Booking.STATUS_PENDING,
    )
    # 2. Rejected booking using 3 units
    b_rejected = Booking(
        user_id=student_user.id,
        equipment_id=sample_equipment.id,
        booking_date=test_date,
        start_time=time(10, 0),
        end_time=time(12, 0),
        quantity=3,
        purpose="Rejected booking",
        status=Booking.STATUS_REJECTED,
    )
    db.session.add_all([b_pending, b_rejected])
    db.session.commit()

    # Since neither is approved, another booking for 3 units should succeed!
    val, err = validate_booking_request(
        equipment=sample_equipment,
        booking_date=test_date,
        start_time=time(10, 0),
        end_time=time(12, 0),
        quantity=3,
        purpose="Fresh request",
    )
    assert val is True
    assert err is None


def test_same_day_past_start_time_rejected(app, sample_equipment):
    """Test that booking for today with a start time in the past is rejected."""
    today = date.today()
    mock_now = datetime.combine(today, time(14, 30))  # 14:30

    # Start time 14:00 (past)
    is_valid, msg = validate_booking_request(
        equipment=sample_equipment,
        booking_date=today,
        start_time=time(14, 0),
        end_time=time(16, 0),
        quantity=1,
        purpose="Past time today",
        current_dt=mock_now,
    )
    assert is_valid is False
    assert "cannot be in the past for today's date" in msg

    # Start time 15:00 (future)
    is_valid_fut, msg_fut = validate_booking_request(
        equipment=sample_equipment,
        booking_date=today,
        start_time=time(15, 0),
        end_time=time(17, 0),
        quantity=1,
        purpose="Future time today",
        current_dt=mock_now,
    )
    assert is_valid_fut is True
    assert msg_fut is None
