"""Staff approval, rejection, and system integration services.

Assigned to: Module M5 – Approval & Integration
Member: Pawani Thathsarani Bandara (Student ID: 6251)

Integrates booking requests created by M3 and applies M4 validation rules
for capacity re-verification upon staff approval.
"""

from database.database import db
from modules.M3_booking_form_model.models import Booking, Equipment, User
from modules.M4_booking_validation.service import validate_approval_capacity


def get_staff_dashboard_metrics() -> dict:
    """Calculate laboratory administrative metrics for staff dashboard."""
    total_equipment = Equipment.query.count()
    operational_equipment = Equipment.query.filter_by(
        status=Equipment.STATUS_AVAILABLE
    ).count()

    pending_bookings = (
        Booking.query.filter_by(status=Booking.STATUS_PENDING)
        .order_by(Booking.created_at.asc())
        .all()
    )
    approved_count = Booking.query.filter_by(
        status=Booking.STATUS_APPROVED
    ).count()
    rejected_count = Booking.query.filter_by(
        status=Booking.STATUS_REJECTED
    ).count()

    recent_requests = pending_bookings[:6]

    return {
        "total_equipment": total_equipment,
        "operational_equipment": operational_equipment,
        "pending_count": len(pending_bookings),
        "approved_count": approved_count,
        "rejected_count": rejected_count,
        "recent_requests": recent_requests,
    }


def get_pending_requests() -> list[Booking]:
    """Retrieve queue of all pending student equipment booking requests."""
    return (
        Booking.query.filter_by(status=Booking.STATUS_PENDING)
        .order_by(Booking.booking_date.asc(), Booking.start_time.asc())
        .all()
    )


def approve_booking_request(
    booking_id: int, staff_user: User
) -> tuple[Booking | None, str | None]:
    """Approve a student's booking request with capacity re-verification (M4 validation).

    Prevents invalid transitions and guarantees capacity availability.
    """
    booking = db.session.get(Booking, booking_id)
    if not booking:
        return None, "Booking request not found."

    if not booking.is_pending:
        return (
            None,
            f"Invalid transition: Booking #{booking.id} is already marked as '{booking.status}'.",
        )

    # Re-verify capacity via Module M4
    is_valid, error_msg = validate_approval_capacity(booking)
    if not is_valid:
        return None, f"Cannot approve Booking #{booking.id}: {error_msg}"

    booking.approve(staff_user)
    db.session.commit()
    return booking, None


def reject_booking_request(
    booking_id: int, staff_user: User, reason: str = ""
) -> tuple[Booking | None, str | None]:
    """Reject a student's booking request with an optional logged reason."""
    booking = db.session.get(Booking, booking_id)
    if not booking:
        return None, "Booking request not found."

    if not booking.is_pending:
        return (
            None,
            f"Invalid transition: Booking #{booking.id} is already marked as '{booking.status}'.",
        )

    booking.reject(staff_user, reason=reason)
    db.session.commit()
    return booking, None


def get_all_bookings_history(
    status_filter: str = "", equipment_filter: int | None = None
) -> tuple[list[Booking], list[Equipment]]:
    """Retrieve filtered historical archive of all bookings across students."""
    query = Booking.query
    if status_filter in Booking.STATUSES:
        query = query.filter(Booking.status == status_filter)
    if equipment_filter:
        query = query.filter(Booking.equipment_id == equipment_filter)

    all_bookings = query.order_by(Booking.created_at.desc()).all()
    all_equipment = Equipment.query.order_by(Equipment.name.asc()).all()

    return all_bookings, all_equipment
