"""Student portal and equipment booking routes.

Assigned to: Module M3 – Booking Form & Model
Member: Imasha Chandralal (Student ID: 6302, GitHub: asp2023145)

Routes:
- GET /student/dashboard: Personal metrics and quick booking access
- GET /student/my-bookings: Personal booking history and status tracking
- GET, POST /student/book: Equipment booking form with M4 validation
- POST /student/bookings/<id>/cancel: Cancel pending booking request
"""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user

from modules.M1_accounts_auth.decorators import student_required
from modules.M3_booking_form_model.models import Booking, Equipment
from modules.M3_booking_form_model.service import (
    cancel_student_booking,
    create_student_booking,
    get_student_bookings,
    get_student_dashboard_metrics,
)

bookings_bp = Blueprint(
    "student", __name__, url_prefix="/student", template_folder="templates"
)


@bookings_bp.route("/dashboard")
@student_required
def dashboard():
    """Student personal portal with booking statistics and recent history."""
    metrics = get_student_dashboard_metrics(current_user.id)
    return render_template(
        "student/dashboard.html",
        **metrics,
    )


@bookings_bp.route("/my-bookings")
@student_required
def my_bookings():
    """View personal booking request history with status filters."""
    status_filter = request.args.get("status", "").strip()
    bookings = get_student_bookings(current_user.id, status_filter=status_filter)

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
    all_equipment = (
        Equipment.query.filter_by(status=Equipment.STATUS_AVAILABLE)
        .order_by(Equipment.name.asc())
        .all()
    )

    if request.method == "POST":
        equipment_id = request.form.get("equipment_id", type=int)
        date_str = request.form.get("booking_date", "").strip()
        start_time_str = request.form.get("start_time", "").strip()
        end_time_str = request.form.get("end_time", "").strip()
        quantity = request.form.get("quantity", type=int, default=1)
        purpose = request.form.get("purpose", "").strip()

        new_booking, error_msg = create_student_booking(
            user_id=current_user.id,
            equipment_id=equipment_id,
            date_str=date_str,
            start_time_str=start_time_str,
            end_time_str=end_time_str,
            quantity=quantity,
            purpose=purpose,
        )

        if error_msg:
            flash(error_msg, "danger")
            if new_booking is not None:
                # Booking was persisted as Rejected — send student to their history.
                flash(
                    "Your booking request has been automatically rejected and saved. "
                    "You can view the reason in your booking history.",
                    "warning",
                )
                return redirect(url_for("student.my_bookings"))
            # Not enough data to persist — re-render the form so the student can fix it.
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

        flash(
            f"Booking request for '{new_booking.equipment.name}' submitted successfully! Status is now Pending Staff Review.",
            "success",
        )
        return redirect(url_for("student.my_bookings"))

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
    success, error_msg = cancel_student_booking(booking_id, current_user.id)

    if not success:
        flash(error_msg, "warning")
        return redirect(url_for("student.my_bookings"))

    flash(f"Booking #{booking_id} has been cancelled.", "info")
    return redirect(url_for("student.my_bookings"))
