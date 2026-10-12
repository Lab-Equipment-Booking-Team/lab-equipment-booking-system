from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError

from models import Booking, Equipment, db
from utils.decorators import student_required
from utils.validators import parse_date, parse_time, validate_booking_request

bookings_bp = Blueprint("student", __name__, url_prefix="/student")


@bookings_bp.route("/dashboard")
@student_required
def dashboard():
    """Student personal portal with booking statistics and recent history."""
    user_bookings = (
        Booking.query.filter_by(user_id=current_user.id)
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

    return render_template(
        "student/dashboard.html",
        pending_count=pending_count,
        approved_count=approved_count,
        rejected_count=rejected_count,
        total_count=total_count,
        recent_bookings=recent_bookings,
        available_equipment=available_equipment,
    )


@bookings_bp.route("/my-bookings")
@student_required
def my_bookings():
    """View personal booking request history with status filters."""
    status_filter = request.args.get("status", "").strip()

    query = Booking.query.filter_by(user_id=current_user.id)
    if status_filter in Booking.STATUSES:
        query = query.filter_by(status=status_filter)

    bookings = query.order_by(Booking.created_at.desc()).all()

    return render_template(
        "student/my_bookings.html",
        bookings=bookings,
        selected_status=status_filter,
        statuses=Booking.STATUSES,
    )


@bookings_bp.route("/book", methods=["GET", "POST"])
@student_required
def create_booking():
    """Submit a new equipment booking request with rigorous server-side validation."""
    preselected_id = request.args.get("equipment_id", type=int)
    all_equipment = Equipment.query.filter_by(
        status=Equipment.STATUS_AVAILABLE
    ).order_by(Equipment.name.asc()).all()

    if request.method == "POST":
        equipment_id = request.form.get("equipment_id", type=int)
        date_str = request.form.get("booking_date", "").strip()
        start_time_str = request.form.get("start_time", "").strip()
        end_time_str = request.form.get("end_time", "").strip()
        quantity = request.form.get("quantity", type=int, default=1)
        purpose = request.form.get("purpose", "").strip()

        equipment = db.session.get(Equipment, equipment_id) if equipment_id else None
        b_date = parse_date(date_str)
        s_time = parse_time(start_time_str)
        e_time = parse_time(end_time_str)

        is_valid, error_msg = validate_booking_request(
            equipment=equipment,
            booking_date=b_date,
            start_time=s_time,
            end_time=e_time,
            quantity=quantity,
            purpose=purpose,
        )

        if not is_valid:
            flash(error_msg, "danger")
            return render_template(
                "student/create_booking.html",
                equipment_list=all_equipment,
                selected_equipment_id=equipment_id,
                date_str=date_str,
                start_time_str=start_time_str,
                end_time_str=end_time_str,
                quantity=quantity,
                purpose=purpose,
            )

        new_booking = Booking(
            user_id=current_user.id,
            equipment_id=equipment.id,
            booking_date=b_date,
            start_time=s_time,
            end_time=e_time,
            quantity=quantity,
            purpose=purpose,
            status=Booking.STATUS_PENDING,
        )

        try:
            db.session.add(new_booking)
            db.session.commit()
            flash(
                f"Booking request for '{equipment.name}' submitted successfully! Status is now Pending Staff Review.",
                "success",
            )
            return redirect(url_for("student.my_bookings"))
        except SQLAlchemyError:
            db.session.rollback()
            flash(
                "An unexpected error occurred while processing your booking request. Please try again.",
                "danger",
            )

    return render_template(
        "student/create_booking.html",
        equipment_list=all_equipment,
        selected_equipment_id=preselected_id,
        quantity=1,
    )


@bookings_bp.route("/bookings/<int:booking_id>/cancel", methods=["POST"])
@student_required
def cancel_booking(booking_id: int):
    """Allow student to cancel a pending booking request."""
    booking = Booking.query.filter_by(
        id=booking_id, user_id=current_user.id
    ).first_or_404()

    if not booking.is_pending:
        flash(
            f"Cannot cancel booking #{booking.id} because its current status is '{booking.status}'.",
            "warning",
        )
        return redirect(url_for("student.my_bookings"))

    booking.cancel()
    db.session.commit()
    flash(f"Booking request #{booking.id} has been cancelled.", "info")
    return redirect(url_for("student.my_bookings"))
