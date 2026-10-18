"""Module M1 – Accounts & Authentication.

Assigned to: Prabhashi Peiris (Student ID: 6308, GitHub: asp2023155)
"""

from modules.M1_accounts_auth.decorators import staff_required, student_required
from modules.M1_accounts_auth.routes import auth_bp
from modules.M1_accounts_auth.service import (
    authenticate_user,
    is_safe_redirect_url,
    register_user,
    validate_registration_fields,
)

__all__ = [
    "auth_bp",
    "authenticate_user",
    "is_safe_redirect_url",
    "register_user",
    "staff_required",
    "student_required",
    "validate_registration_fields",
]
