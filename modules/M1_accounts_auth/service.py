"""Authentication and user management services.

Assigned to: Module M1 – Accounts & Authentication
Member: Prabhashi Peiris (Student ID: 6308, GitHub: asp2023155)

Handles user credential verification, secure password hashing,
registration validation, and safe URL redirection checks.
"""

import re
from urllib.parse import urlsplit

from sqlalchemy.exc import SQLAlchemyError

from database.database import db
from modules.M3_booking_form_model.models import User


def is_safe_redirect_url(target: str, host_url: str) -> bool:
    """Ensure redirect URL belongs to local application to prevent open redirects."""
    if not target:
        return False
    ref_url = urlsplit(host_url)
    test_url = urlsplit(target)
    return (
        test_url.scheme in ("http", "https")
        and ref_url.netloc == test_url.netloc
        or not test_url.netloc
    )


def validate_registration_fields(
    username: str,
    email: str,
    full_name: str,
    student_or_staff_id: str,
    password: str,
    confirm_password: str,
) -> tuple[bool, str | None]:
    """Validate user registration field inputs."""
    if (
        not username
        or not email
        or not full_name
        or not student_or_staff_id
        or not password
    ):
        return False, "All required fields must be completed."

    if len(username) < 3 or len(username) > 30:
        return False, "Username must be between 3 and 30 characters long."

    if not re.match(r"^[a-zA-Z0-9_.-]+$", username):
        return False, "Username may only contain letters, numbers, dots, and underscores."

    if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
        return False, "Please enter a valid email address."

    if len(password) < 6:
        return False, "Password must be at least 6 characters long."

    if password != confirm_password:
        return False, "Passwords do not match. Please verify and try again."

    if User.query.filter_by(username=username).first():
        return False, f"The username '{username}' is already in use. Please choose another."

    if User.query.filter_by(email=email).first():
        return False, f"The email address '{email}' is already registered."

    return True, None


def register_user(
    username: str,
    email: str,
    full_name: str,
    student_or_staff_id: str,
    password: str,
    confirm_password: str,
    staff_key: str = "",
    configured_staff_key: str | None = None,
) -> tuple[User | None, str | None]:
    """Register a new user account with secure password hashing.

    Public registration creates Student accounts by default.
    Staff accounts require a valid staff registration key.
    """
    is_valid, error_msg = validate_registration_fields(
        username=username,
        email=email,
        full_name=full_name,
        student_or_staff_id=student_or_staff_id,
        password=password,
        confirm_password=confirm_password,
    )
    if not is_valid:
        return None, error_msg

    assigned_role = User.ROLE_STUDENT
    if staff_key:
        if configured_staff_key and staff_key == configured_staff_key:
            assigned_role = User.ROLE_STAFF
        else:
            return False, "Invalid Staff Registration Key. Staff account registration failed."

    new_user = User(
        username=username,
        email=email,
        full_name=full_name,
        student_or_staff_id=student_or_staff_id,
        role=assigned_role,
    )
    new_user.set_password(password)

    try:
        db.session.add(new_user)
        db.session.commit()
        return new_user, None
    except SQLAlchemyError:
        db.session.rollback()
        return None, "An unexpected error occurred while saving the account. Please try again."


def authenticate_user(identifier: str, password: str) -> tuple[User | None, str | None]:
    """Authenticate a user by username or email and password."""
    if not identifier or not password:
        return None, "Please enter both username/email and your password."

    user = User.query.filter(
        (User.username == identifier) | (User.email == identifier.lower())
    ).first()

    if not user or not user.check_password(password):
        return None, "Invalid credentials. Please verify your username and password."

    return user, None
