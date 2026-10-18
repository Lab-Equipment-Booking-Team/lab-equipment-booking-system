"""Module M2 – Equipment Catalogue.

Assigned to: Shashinika Rathnayaka (Student ID: 6312, GitHub: Shashithathsarani2003)
"""

from modules.M2_equipment_catalogue.routes import equipment_bp
from modules.M2_equipment_catalogue.service import (
    add_equipment,
    check_equipment_availability,
    delete_equipment,
    get_catalogue,
    get_equipment_by_id,
    update_equipment,
)

__all__ = [
    "add_equipment",
    "check_equipment_availability",
    "delete_equipment",
    "equipment_bp",
    "get_catalogue",
    "get_equipment_by_id",
    "update_equipment",
]
