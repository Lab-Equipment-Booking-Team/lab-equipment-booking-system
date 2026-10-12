from datetime import date, datetime, time

from models import Booking, Equipment


def parse_date(date_str: str) -> date | None:
    """Safely parse YYYY-MM-DD date string."""
    try:
        return datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
    except (ValueError, AttributeError):
        return None


def parse_time(time_str: str) -> time | None:
    """Safely parse HH:MM (24-hour) time string."""
    try:
        return datetime.strptime(time_str.strip(), "%H:%M").time()
    except (ValueError, AttributeError):
        return None


def get_conflicting_approved_bookings(
    equipment_id: int,
    booking_date: date,
    start_time: time,
    end_time: time,
    exclude_booking_id: int | None = None,
) -> list[Booking]:
    """Retrieve all approved bookings on the same date that overlap with the time range.
    Two intervals [s1, e1) and [s2, e2) overlap if:
    s1 < e2 and e1 > s2.
    """
    query = Booking.query.filter(
        Booking.equipment_id == equipment_id,
        Booking.booking_date == booking_date,
        Booking.status == Booking.STATUS_APPROVED,
        Booking.start_time < end_time,
        Booking.end_time > start_time,
    )
    if exclude_booking_id is not None:
        query = query.filter(Booking.id != exclude_booking_id)

    return query.all()


def calculate_peak_booked_quantity(
    equipment_id: int,
    booking_date: date,
    start_time: time,
    end_time: time,
    exclude_booking_id: int | None = None,
) -> int:
    """Calculate the maximum quantity of equipment currently booked concurrently

    during the specified date and time interval.
    """
    conflicting = get_conflicting_approved_bookings(
        equipment_id=equipment_id,
        booking_date=booking_date,
        start_time=start_time,
        end_time=end_time,
        exclude_booking_id=exclude_booking_id,
    )

    if not conflicting:
        return 0

    # Test critical points: interval start and all overlapping booking starts
    critical_points = {start_time}
    for b in conflicting:
        if start_time <= b.start_time < end_time:
            critical_points.add(b.start_time)

    peak = 0
    for cp in critical_points:
        active_sum = sum(
            b.quantity
            for b in conflicting
            if b.start_time <= cp < b.end_time
        )
        peak = max(peak, active_sum)

    return peak


def validate_booking_request(
    equipment: Equipment | None,
    booking_date: date | None,
    start_time: time | None,
    end_time: time | None,
    quantity: int,
    purpose: str,
    exclude_booking_id: int | None = None,
    current_dt: datetime | None = None,
) -> tuple[bool, str | None]:
    """Validate all business rules for a booking request.

    Returns:
        (is_valid: bool, error_message: Optional[str])
    """
    if equipment is None:
        return False, "The selected laboratory equipment does not exist."

    if not equipment.is_operational:
        return (
            False,
            f"'{equipment.name}' is currently {equipment.status.lower()} and cannot be booked.",
        )

    if not booking_date:
        return False, "Please specify a valid booking date (YYYY-MM-DD)."

    if not start_time or not end_time:
        return False, "Please specify both start time and end time."

    if start_time >= end_time:
        return (
            False,
            f"The start time ({start_time.strftime('%H:%M')}) must be strictly earlier than the end time ({end_time.strftime('%H:%M')}).",
        )

    # Current date and time check for past booking prevention
    now = current_dt or datetime.now()
    today = now.date()
    current_time = now.time()

    if booking_date < today:
        return (
            False,
            f"Booking date cannot be in the past ({booking_date.strftime('%Y-%m-%d')}).",
        )

    if booking_date == today and start_time <= current_time:
        return (
            False,
            f"The start time ({start_time.strftime('%H:%M')}) cannot be in the past for today's date.",
        )

    if not isinstance(quantity, int) or quantity <= 0:
        return False, "Requested quantity must be a positive integer (at least 1)."

    if quantity > equipment.quantity_available:
        return (
            False,
            f"Requested quantity ({quantity}) exceeds total equipment inventory ({equipment.quantity_available}).",
        )

    if not purpose or not purpose.strip():
        return False, "Please provide a clear purpose or project reason for the booking."

    # Check capacity against overlapping approved bookings
    peak_booked = calculate_peak_booked_quantity(
        equipment_id=equipment.id,
        booking_date=booking_date,
        start_time=start_time,
        end_time=end_time,
        exclude_booking_id=exclude_booking_id,
    )

    remaining_available = equipment.quantity_available - peak_booked
    if remaining_available < quantity:
        err_msg = (
            f"Capacity conflict: For the selected time slot ({start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}), "
            f"only {remaining_available} unit(s) remain available out of {equipment.quantity_available} (already booked: {peak_booked})."
        )
        return False, err_msg

    return True, None
