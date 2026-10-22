"""Equipment Catalogue and Inventory routes.

Assigned to: Module M2 – Equipment Catalogue
Member: Shashinika Rathnayaka (Student ID: 6312, GitHub: Shashithathsarani2003)

Routes:
- GET /equipment: Responsive equipment catalogue with search and filter
- GET /equipment/<id>: Detailed specifications view
- GET /equipment/api/check-availability: Live slot availability check API
"""

from flask import Blueprint, jsonify, render_template, request

from database.database import db
from modules.M2_equipment_catalogue.service import (
    check_equipment_availability,
    get_catalogue,
)
from modules.M3_booking_form_model.models import Equipment

equipment_bp = Blueprint(
    "equipment", __name__, url_prefix="/equipment", template_folder="templates"
)


@equipment_bp.route("")
def catalogue():
    """Display equipment catalogue with search, filter, and responsive view."""
    query_text = request.args.get("q", "").strip()
    category_filter = request.args.get("category", "").strip()
    status_filter = request.args.get("status", "").strip()

    equipment_list, available_categories = get_catalogue(
        query_text=query_text,
        category_filter=category_filter,
        status_filter=status_filter,
    )

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

    success, result = check_equipment_availability(
        equipment_id=equipment_id,
        date_str=date_str,
        start_str=start_str,
        end_str=end_str,
    )

    if not success:
        return jsonify({"success": False, "error": result}), 400

    return jsonify({"success": True, **result})
