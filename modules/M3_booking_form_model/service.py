"""Booking creation and student booking services.

Assigned to: Module M3 – Booking Form & Model
Member: Imasha Chandralal (Student ID: 6302, GitHub: asp2023145)

Manages student booking request creation, Pending status initialisation,
booking cancellation, and student dashboard/history data aggregation.
Integrates with Module M4 for server-side booking validation.
"""

from database.database import db
from modules.M3_booking_form_model.models import Booking, Equipment
from modules.M4_booking_validation.service import validate_booking_submission
from modules.M4_booking_validation.validation import parse_date, parse_time


def get_student_dashboard_metrics(user_id: int) -> dict:
    """Calculate summary statistics and load recent bookings for a student."""
    user_bookings = (
        Booking.query.filter_by(user_id=user_id)
        .order_by(Booking.created_at.desc())
        .all()
    )

    pending_count = sum(1 for b in user_bookings if b.is_pending)
    approved_count = sum(1 for b in user_bookings if b.is_approved)
    rejected_count = sum(1 for b in user_bookings if b.is_rejected)
    total_count = len(user_bookings)

    recent_bookings = user_bookings[:5]
    available_equipment = (
        Equipment.query.filter_by(status=Equipment.STATUS_AVAILABLE)
        .order_by(Equipment.name.asc())
        .limit(4)
        .all()
    )

    return {
        "pending_count": pending_count,
        "approved_count": approved_count,
        "rejected_count": rejected_count,
        "total_count": total_count,
        "recent_bookings": recent_bookings,
        "available_equipment": available_equipment,
    }


def get_student_bookings(user_id: int, status_filter: str = "") -> list[Booking]:
    """Retrieve filtered booking request history for a student."""
    query = Booking.query.filter_by(user_id=user_id)
    if status_filter in Booking.STATUSES:
        query = query.filter_by(status=status_filter)
    return query.order_by(Booking.created_at.desc()).all()


def create_student_booking(
    user_id: int,
    equipment_id: int | None,
    date_str: str,
    start_time_str: str,
    end_time_str: str,
    quantity: int,
    purpose: str,
) -> tuple[Booking | None, str | None]:
    """Validate and create a new student equipment booking request.

    Uses Module M4 (Booking Validation) to enforce all business constraints
    and initialises the status to 'Pending' staff review.
    """
    equipment = db.session.get(Equipment, equipment_id) if equipment_id else None
    b_date = parse_date(date_str)
    s_time = parse_time(start_time_str)
    e_time = parse_time(end_time_str)

    # Enforce business validation via Module M4
    is_valid, error_msg = validate_booking_submission(
        equipment=equipment,
        booking_date=b_date,
        start_time=s_time,
        end_time=e_time,
        quantity=quantity,
        purpose=purpose,
    )

    if not is_valid:
        return None, error_msg

    new_booking = Booking(
        user_id=user_id,
        equipment_id=equipment.id,
        booking_date=b_date,
        start_time=s_time,
        end_time=e_time,
        quantity=quantity,
        purpose=purpose,
        status=Booking.STATUS_PENDING,
    )

    db.session.add(new_booking)
    db.session.commit()
    return new_booking, None


def cancel_student_booking(booking_id: int, user_id: int) -> tuple[bool, str | None]:
    """Allow a student to cancel their own pending booking request."""
    booking = Booking.query.filter_by(
        id=booking_id, user_id=user_id
    ).first()

    if not booking:
        return False, "Booking request not found."

    if not booking.is_pending:
        return (
            False,
            f"Cannot cancel booking #{booking.id} because its current status is '{booking.status}'.",
        )

    booking.cancel()
    db.session.commit()
    return True, None
