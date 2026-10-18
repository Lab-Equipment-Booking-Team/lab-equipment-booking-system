"""Staff approval, rejection, and administrative routing endpoints.

Assigned to: Module M5 – Approval & Integration
Member: Pawani Thathsarani Bandara (Student ID: 6251)

Routes:
- GET /staff/dashboard: Overall lab operations overview
- GET /staff/requests/pending: Pending student booking request queue
- POST /staff/requests/<id>/approve: Approve booking request with capacity check
- POST /staff/requests/<id>/reject: Reject booking request with optional reason
- GET /staff/bookings/history: Comprehensive booking history archive
- Equipment CRUD routes integrated with Module M2 services
"""

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user

from database.database import db
from modules.M1_accounts_auth.decorators import staff_required
from modules.M2_equipment_catalogue import service as equipment_service
from modules.M3_booking_form_model.models import Booking, Equipment
from modules.M5_approval_integration.service import (
    approve_booking_request,
    get_all_bookings_history,
    get_pending_requests,
    get_staff_dashboard_metrics,
    reject_booking_request,
)

staff_bp = Blueprint("staff", __name__, url_prefix="/staff", template_folder="templates")


@staff_bp.route("/dashboard")
@staff_required
def dashboard():
    """Staff administrative control dashboard."""
    metrics = get_staff_dashboard_metrics()
    return render_template(
        "staff/dashboard.html",
        **metrics,
    )


@staff_bp.route("/requests/pending")
@staff_required
def pending_requests():
    """Queue of all pending student equipment booking requests."""
    pending_list = get_pending_requests()
    return render_template(
        "staff/pending_requests.html",
        pending_list=pending_list,
    )


@staff_bp.route("/requests/<int:booking_id>/approve", methods=["POST"])
@staff_required
def approve_request(booking_id: int):
    """Approve a student's booking request with capacity re-verification."""
    booking, error_msg = approve_booking_request(booking_id, current_user)

    if error_msg:
        flash(error_msg, "danger" if "Cannot approve" in error_msg else "warning")
        return redirect(url_for("staff.pending_requests"))

    flash(
        f"Booking #{booking.id} for {booking.user.full_name} ({booking.equipment.name}) has been Approved.",
        "success",
    )
    return redirect(url_for("staff.pending_requests"))


@staff_bp.route("/requests/<int:booking_id>/reject", methods=["POST"])
@staff_required
def reject_request(booking_id: int):
    """Reject a student's booking request with an optional reason."""
    reason = request.form.get("rejection_reason", "").strip()
    booking, error_msg = reject_booking_request(booking_id, current_user, reason=reason)

    if error_msg:
        flash(error_msg, "warning")
        return redirect(url_for("staff.pending_requests"))

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

    all_bookings, all_equipment = get_all_bookings_history(
        status_filter=status_filter,
        equipment_filter=equipment_filter,
    )

    return render_template(
        "staff/all_bookings.html",
        bookings=all_bookings,
        selected_status=status_filter,
        selected_equipment_id=equipment_filter,
        all_equipment=all_equipment,
        statuses=Booking.STATUSES,
    )


# --- Equipment Management Routes (delegates to Module M2 services) ---


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
    """Register new equipment in the lab inventory using Module M2 service."""
    if request.method == "POST":
        code = request.form.get("code", "").strip().upper()
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()
        quantity_str = request.form.get("quantity_available", "").strip()
        status = request.form.get("status", Equipment.STATUS_AVAILABLE).strip()

        item, error_msg = equipment_service.add_equipment(
            code=code,
            name=name,
            category=category,
            description=description,
            quantity_str=quantity_str,
            status=status,
        )

        if error_msg:
            flash(error_msg, "danger")
            return render_template("staff/equipment_form.html", is_edit=False)

        flash(f"Equipment '{item.name}' ({item.code}) added successfully!", "success")
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
    """Edit existing equipment details using Module M2 service."""
    item = db.get_or_404(Equipment, equipment_id)

    if request.method == "POST":
        code = request.form.get("code", "").strip().upper()
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        description = request.form.get("description", "").strip()
        quantity_str = request.form.get("quantity_available", "").strip()
        status = request.form.get("status", "").strip()

        updated_item, error_msg = equipment_service.update_equipment(
            equipment_id=equipment_id,
            code=code,
            name=name,
            category=category,
            description=description,
            quantity_str=quantity_str,
            status=status,
        )

        if error_msg:
            flash(error_msg, "danger")
            return render_template(
                "staff/equipment_form.html", is_edit=True, item=item
            )

        flash(f"Equipment '{updated_item.name}' updated successfully.", "success")
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
    name = item.name
    code = item.code

    success, error_msg = equipment_service.delete_equipment(equipment_id)
    if not success:
        flash(error_msg, "danger")
        return redirect(url_for("staff.manage_equipment"))

    flash(f"Equipment '{name}' ({code}) has been deleted successfully.", "success")
    return redirect(url_for("staff.manage_equipment"))
