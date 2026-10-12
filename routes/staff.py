from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user

from models import Booking, Equipment, db
from utils.decorators import staff_required
from utils.validators import validate_booking_request

staff_bp = Blueprint("staff", __name__, url_prefix="/staff")


@staff_bp.route("/dashboard")
@staff_required
def dashboard():
    """Staff administrative control dashboard."""
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

    return render_template(
        "staff/dashboard.html",
        total_equipment=total_equipment,
        operational_equipment=operational_equipment,
        pending_count=len(pending_bookings),
        approved_count=approved_count,
        rejected_count=rejected_count,
        recent_requests=recent_requests,
    )


@staff_bp.route("/requests/pending")
@staff_required
def pending_requests():
    """Queue of all pending student equipment booking requests."""
    pending_list = (
        Booking.query.filter_by(status=Booking.STATUS_PENDING)
        .order_by(Booking.booking_date.asc(), Booking.start_time.asc())
        .all()
    )
    return render_template(
        "staff/pending_requests.html",
        pending_list=pending_list,
    )


@staff_bp.route("/requests/<int:booking_id>/approve", methods=["POST"])
@staff_required
def approve_request(booking_id: int):
    """Approve a student's booking request with capacity re-verification."""
    booking = db.get_or_404(Booking, booking_id)

    if not booking.is_pending:
        flash(
            f"Invalid transition: Booking #{booking.id} is already marked as '{booking.status}'.",
            "warning",
        )
        return redirect(url_for("staff.pending_requests"))

    # Re-verify that approving this booking will not exceed available capacity
    is_valid, error_msg = validate_booking_request(
        equipment=booking.equipment,
        booking_date=booking.booking_date,
        start_time=booking.start_time,
        end_time=booking.end_time,
        quantity=booking.quantity,
        purpose=booking.purpose,
        exclude_booking_id=booking.id,
    )

    if not is_valid:
        flash(
            f"Cannot approve Booking #{booking.id}: {error_msg}",
            "danger",
        )
        return redirect(url_for("staff.pending_requests"))

    booking.approve(current_user)
    db.session.commit()
    flash(
        f"Booking #{booking.id} for {booking.user.full_name} ({booking.equipment.name}) has been Approved.",
        "success",
    )
    return redirect(url_for("staff.pending_requests"))


@staff_bp.route("/requests/<int:booking_id>/reject", methods=["POST"])
@staff_required
def reject_request(booking_id: int):
    """Reject a student's booking request with an optional reason."""
    booking = db.get_or_404(Booking, booking_id)

    if not booking.is_pending:
        flash(
            f"Invalid transition: Booking #{booking.id} is already marked as '{booking.status}'.",
            "warning",
        )
        return redirect(url_for("staff.pending_requests"))

    reason = request.form.get("rejection_reason", "").strip()
    booking.reject(current_user, reason=reason)
    db.session.commit()
    flash(
        f"Booking #{booking.id} has been Rejected. Reason logged: {reason or 'No reason specified'}.",
        "info",
    )
    return redirect(url_for("staff.pending_requests"))


@staff_bp.route("/bookings/history")
@staff_required
def booking_history():
    """Complete booking archive across all students and statuses."""
    status_filter = request.args.get("status", "").strip()
    equipment_filter = request.args.get("equipment_id", type=int)

    query = Booking.query
    if status_filter in Booking.STATUSES:
        query = query.filter(Booking.status == status_filter)
    if equipment_filter:
        query = query.filter(Booking.equipment_id == equipment_filter)

    all_bookings = query.order_by(Booking.created_at.desc()).all()
    all_equipment = Equipment.query.order_by(Equipment.name.asc()).all()

    return render_template(
        "staff/all_bookings.html",
        bookings=all_bookings,
        selected_status=status_filter,
        selected_equipment_id=equipment_filter,
        all_equipment=all_equipment,
        statuses=Booking.STATUSES,
    )


# --- Equipment Management Routes (M2 - FR-01) ---


@staff_bp.route("/equipment")
@staff_required
def manage_equipment():
    """Staff equipment inventory management."""
    equipment_list = Equipment.query.order_by(Equipment.name.asc()).all()
    return render_template(
        "staff/manage_equipment.html",
        equipment_list=equipment_list,
    )


@staff_bp.route("/equipment/new", methods=["GET", "POST"])
@staff_required
def add_equipment():
    """Register new equipment in the lab inventory."""
    if request.method == "POST":
        code = request.form.get("code", "").strip().upper()
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()
        quantity_str = request.form.get("quantity_available", "").strip()
        status = request.form.get("status", Equipment.STATUS_AVAILABLE).strip()

        # Validation
        if not code or not name or not category or not quantity_str:
            flash("Equipment code, name, category, and quantity are required.", "danger")
            return render_template("staff/equipment_form.html", is_edit=False)

        try:
            quantity = int(quantity_str)
            if quantity < 1:
                flash("Quantity available must be at least 1.", "danger")
                return render_template("staff/equipment_form.html", is_edit=False)
        except ValueError:
            flash("Quantity must be a valid whole number.", "danger")
            return render_template("staff/equipment_form.html", is_edit=False)

        if Equipment.query.filter_by(code=code).first():
            flash(f"Equipment code '{code}' is already registered. Codes must be unique.", "danger")
            return render_template("staff/equipment_form.html", is_edit=False)

        if status not in Equipment.STATUSES:
            flash("Invalid equipment status selection.", "danger")
            return render_template("staff/equipment_form.html", is_edit=False)

        new_item = Equipment(
            code=code,
            name=name,
            category=category,
            description=description,
            quantity_available=quantity,
            status=status,
        )

        db.session.add(new_item)
        db.session.commit()
        flash(f"Equipment '{new_item.name}' ({new_item.code}) added successfully!", "success")
        return redirect(url_for("staff.manage_equipment"))

    return render_template(
        "staff/equipment_form.html",
        is_edit=False,
        categories=Equipment.CATEGORIES,
        statuses=Equipment.STATUSES,
    )


@staff_bp.route("/equipment/<int:equipment_id>/edit", methods=["GET", "POST"])
@staff_required
def edit_equipment(equipment_id: int):
    """Edit existing equipment details."""
    item = db.get_or_404(Equipment, equipment_id)

    if request.method == "POST":
        code = request.form.get("code", "").strip().upper()
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()
        quantity_str = request.form.get("quantity_available", "").strip()
        status = request.form.get("status", "").strip()

        if not code or not name or not category or not quantity_str:
            flash("Equipment code, name, category, and quantity are required.", "danger")
            return render_template("staff/equipment_form.html", is_edit=True, item=item)

        try:
            quantity = int(quantity_str)
            if quantity < 1:
                flash("Quantity available must be at least 1.", "danger")
                return render_template("staff/equipment_form.html", is_edit=True, item=item)
        except ValueError:
            flash("Quantity must be a valid whole number.", "danger")
            return render_template("staff/equipment_form.html", is_edit=True, item=item)

        # Ensure code uniqueness excluding self
        existing = Equipment.query.filter_by(code=code).first()
        if existing and existing.id != item.id:
            flash(f"Equipment code '{code}' is already assigned to another item.", "danger")
            return render_template("staff/equipment_form.html", is_edit=True, item=item)

        if status not in Equipment.STATUSES:
            flash("Invalid equipment status selection.", "danger")
            return render_template("staff/equipment_form.html", is_edit=True, item=item)

        item.code = code
        item.name = name
        item.category = category
        item.description = description
        item.quantity_available = quantity
        item.status = status

        db.session.commit()
        flash(f"Equipment '{item.name}' updated successfully.", "success")
        return redirect(url_for("staff.manage_equipment"))

    return render_template(
        "staff/equipment_form.html",
        is_edit=True,
        item=item,
        categories=Equipment.CATEGORIES,
        statuses=Equipment.STATUSES,
    )


@staff_bp.route("/equipment/<int:equipment_id>/delete", methods=["POST"])
@staff_required
def delete_equipment(equipment_id: int):
    """Delete equipment only when deletion will not break existing booking records."""
    item = db.get_or_404(Equipment, equipment_id)

    if not item.can_be_deleted():
        booking_count = len(item.bookings)
        flash(
            f"Cannot delete '{item.name}' ({item.code}) because {booking_count} booking record(s) "
            "reference this equipment. To prevent future reservations without breaking historical records, "
            "please set its status to 'Decommissioned' or 'Under Maintenance' instead.",
            "danger",
        )
        return redirect(url_for("staff.manage_equipment"))

    name = item.name
    code = item.code
    db.session.delete(item)
    db.session.commit()
    flash(f"Equipment '{name}' ({code}) has been deleted successfully.", "success")
    return redirect(url_for("staff.manage_equipment"))
