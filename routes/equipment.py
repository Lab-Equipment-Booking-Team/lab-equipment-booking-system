from flask import Blueprint, jsonify, render_template, request

from models import Equipment, db
from utils.validators import calculate_peak_booked_quantity, parse_date, parse_time

equipment_bp = Blueprint("equipment", __name__, url_prefix="/equipment")


@equipment_bp.route("")
def catalogue():
    """Display equipment catalogue with search, filter, and responsive view."""
    query_text = request.args.get("q", "").strip()
    category_filter = request.args.get("category", "").strip()
    status_filter = request.args.get("status", "").strip()

    query = Equipment.query

    if query_text:
        search_pattern = f"%{query_text}%"
        query = query.filter(
            (Equipment.name.ilike(search_pattern))
            | (Equipment.code.ilike(search_pattern))
            | (Equipment.description.ilike(search_pattern))
        )

    if category_filter:
        query = query.filter(Equipment.category == category_filter)

    if status_filter:
        query = query.filter(Equipment.status == status_filter)

    equipment_list = query.order_by(Equipment.name.asc()).all()

    # Distinct categories for the filter dropdown
    available_categories = [
        c[0]
        for c in Equipment.query.with_entities(Equipment.category)
        .distinct()
        .order_by(Equipment.category.asc())
        .all()
    ]

    return render_template(
        "equipment/catalogue.html",
        equipment_list=equipment_list,
        categories=available_categories,
        selected_category=category_filter,
        selected_status=status_filter,
        query_text=query_text,
    )


@equipment_bp.route("/<int:equipment_id>")
def detail(equipment_id: int):
    """View detailed specs and availability status for a single piece of equipment."""
    item = db.get_or_404(Equipment, equipment_id)
    return render_template("equipment/detail.html", item=item)


@equipment_bp.route("/api/check-availability")
def api_check_availability():
    """API endpoint to calculate available quantity for an equipment at a specific date and time slot."""
    equipment_id = request.args.get("equipment_id", type=int)
    date_str = request.args.get("date")
    start_str = request.args.get("start_time")
    end_str = request.args.get("end_time")

    if not equipment_id or not date_str or not start_str or not end_str:
        return jsonify({"success": False, "error": "Missing parameters"}), 400

    equipment = db.session.get(Equipment, equipment_id)
    if not equipment:
        return jsonify({"success": False, "error": "Equipment not found"}), 404

    b_date = parse_date(date_str)
    s_time = parse_time(start_str)
    e_time = parse_time(end_str)

    if not b_date or not s_time or not e_time:
        return jsonify({"success": False, "error": "Invalid date or time format"}), 400

    if s_time >= e_time:
        return (
            jsonify(
                {"success": False, "error": "Start time must be earlier than end time"}
            ),
            400,
        )

    peak_booked = calculate_peak_booked_quantity(
        equipment_id=equipment.id,
        booking_date=b_date,
        start_time=s_time,
        end_time=e_time,
    )

    remaining = max(0, equipment.quantity_available - peak_booked)

    return jsonify(
        {
            "success": True,
            "equipment_id": equipment.id,
            "total_inventory": equipment.quantity_available,
            "already_booked": peak_booked,
            "available_quantity": remaining,
        }
    )
