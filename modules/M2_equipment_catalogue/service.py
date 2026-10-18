"""Equipment Catalogue and Inventory Management Services.

Assigned to: Module M2 – Equipment Catalogue
Member: Shashinika Rathnayaka (Student ID: 6312, GitHub: Shashithathsarani2003)

Manages laboratory equipment display, search and filtering, inventory CRUD
operations, and availability checks.
"""

from database.database import db
from modules.M3_booking_form_model.models import Equipment
from modules.M4_booking_validation.service import check_slot_availability


def get_catalogue(
    query_text: str = "",
    category_filter: str = "",
    status_filter: str = "",
) -> tuple[list[Equipment], list[str]]:
    """Query equipment list with keyword search, category filter, and status filter."""
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

    return equipment_list, available_categories


def get_equipment_by_id(equipment_id: int) -> Equipment | None:
    """Retrieve an equipment item by its database ID."""
    return db.session.get(Equipment, equipment_id)


def add_equipment(
    code: str,
    name: str,
    category: str,
    description: str,
    quantity_str: str,
    status: str = Equipment.STATUS_AVAILABLE,
) -> tuple[Equipment | None, str | None]:
    """Validate and register a new piece of equipment in the laboratory inventory."""
    if not code or not name or not category or not quantity_str:
        return None, "Equipment code, name, category, and quantity are required."

    try:
        quantity = int(quantity_str)
        if quantity < 1:
            return None, "Quantity available must be at least 1."
    except (ValueError, TypeError):
        return None, "Quantity must be a valid whole number."

    if Equipment.query.filter_by(code=code).first():
        return None, f"Equipment code '{code}' is already registered. Codes must be unique."

    if status not in Equipment.STATUSES:
        return None, "Invalid equipment status selection."

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
    return new_item, None


def update_equipment(
    equipment_id: int,
    code: str,
    name: str,
    category: str,
    description: str,
    quantity_str: str,
    status: str,
) -> tuple[Equipment | None, str | None]:
    """Validate and update an existing piece of equipment."""
    item = db.session.get(Equipment, equipment_id)
    if not item:
        return None, "Equipment not found."

    if not code or not name or not category or not quantity_str:
        return None, "Equipment code, name, category, and quantity are required."

    try:
        quantity = int(quantity_str)
        if quantity < 1:
            return None, "Quantity available must be at least 1."
    except (ValueError, TypeError):
        return None, "Quantity must be a valid whole number."

    existing = Equipment.query.filter_by(code=code).first()
    if existing and existing.id != item.id:
        return None, f"Equipment code '{code}' is already assigned to another item."

    if status not in Equipment.STATUSES:
        return None, "Invalid equipment status selection."

    item.code = code
    item.name = name
    item.category = category
    item.description = description
    item.quantity_available = quantity
    item.status = status

    db.session.commit()
    return item, None


def delete_equipment(equipment_id: int) -> tuple[bool, str | None]:
    """Delete equipment only if no existing booking records reference it."""
    item = db.session.get(Equipment, equipment_id)
    if not item:
        return False, "Equipment not found."

    if not item.can_be_deleted():
        booking_count = len(item.bookings)
        return False, (
            f"Cannot delete '{item.name}' ({item.code}) because {booking_count} booking record(s) "
            "reference this equipment. To prevent future reservations without breaking historical records, "
            "please set its status to 'Decommissioned' or 'Under Maintenance' instead."
        )

    db.session.delete(item)
    db.session.commit()
    return True, None


def check_equipment_availability(
    equipment_id: int,
    date_str: str,
    start_str: str,
    end_str: str,
) -> tuple[bool, dict | str]:
    """Check availability for an equipment item at a specific time slot (uses M4 validation)."""
    return check_slot_availability(equipment_id, date_str, start_str, end_str)
