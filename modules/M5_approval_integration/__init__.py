"""Module M5 – Approval & Integration.

Assigned to: Pawani Thathsarani Bandara (Student ID: 6251)
"""

from modules.M5_approval_integration.routes import staff_bp
from modules.M5_approval_integration.service import (
    approve_booking_request,
    get_all_bookings_history,
    get_pending_requests,
    get_staff_dashboard_metrics,
    reject_booking_request,
)

__all__ = [
    "approve_booking_request",
    "get_all_bookings_history",
    "get_pending_requests",
    "get_staff_dashboard_metrics",
    "reject_booking_request",
    "staff_bp",
]
