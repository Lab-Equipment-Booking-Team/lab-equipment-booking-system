"""Validation service functions for Lab Equipment Booking System.

Assigned to: Module M4 – Booking Validation & QA
Member: Hashini Wickramasinghe (Student ID: 6317, GitHub: Hashini-123)

Provides reusable validation services consumed by M3 (Booking Form Submission)
and M5 (Staff Approval & Integration).
"""

from datetime import date, datetime, time

from database.database import db
from modules.M3_booking_form_model.models import Booking, Equipment
from modules.M4_booking_validation.validation import (
    calculate_peak_booked_quantity,
    parse_date,
    parse_time,
    validate_booking_request,
)


def validate_booking_submission(
    equipment: Equipment | None,
    booking_date: date | None,
    start_time: time | None,
    end_time: time | None,
    quantity: int,
    purpose: str,
    exclude_booking_id: int | None = None,
    current_dt: datetime | None = None,
) -> tuple[bool, str | None]:
    """Validate a booking request prior to creation or persistence.

    Consumed by Module M3 (create_booking).
    """
    return validate_booking_request(
        equipment=equipment,
        booking_date=booking_date,
        start_time=start_time,
        end_time=end_time,
        quantity=quantity,
        purpose=purpose,
        exclude_booking_id=exclude_booking_id,
        current_dt=current_dt,
    )


def check_slot_availability(
    equipment_id: int,
    date_str: str,
    start_str: str,
    end_str: str,
) -> tuple[bool, dict | str]:
    """Check availability for a given equipment and time slot.

    Consumed by Module M2 API (/equipment/api/check-availability).
    """
    equipment = db.session.get(Equipment, equipment_id)
    if not equipment:
        return False, "Equipment not found"

    b_date = parse_date(date_str)
    s_time = parse_time(start_str)
    e_time = parse_time(end_str)

    if not b_date or not s_time or not e_time:
        return False, "Invalid date or time format"

    if s_time >= e_time:
        return False, "Start time must be earlier than end time"

    peak_booked = calculate_peak_booked_quantity(
        equipment_id=equipment.id,
        booking_date=b_date,
        start_time=s_time,
        end_time=e_time,
    )
    remaining = max(0, equipment.quantity_available - peak_booked)

    return True, {
        "equipment_id": equipment.id,
        "total_inventory": equipment.quantity_available,
        "already_booked": peak_booked,
        "available_quantity": remaining,
    }


def validate_approval_capacity(booking: Booking) -> tuple[bool, str | None]:
    """Re-validate that approving this booking will not exceed available capacity.

    Consumed by Module M5 (approve_request).
    """
    return validate_booking_request(
        equipment=booking.equipment,
        booking_date=booking.booking_date,
        start_time=booking.start_time,
        end_time=booking.end_time,
        quantity=booking.quantity,
        purpose=booking.purpose,
        exclude_booking_id=booking.id,
    )
