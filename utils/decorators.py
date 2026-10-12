from functools import wraps

from flask import abort, flash, redirect, request, url_for
from flask_login import current_user


def staff_required(f):
    """Decorator to restrict view access to authenticated staff members only."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in to access staff administration.", "warning")
            return redirect(url_for("auth.login", next=request.url))
        if not current_user.is_staff_member:
            flash(
                "Access denied: Staff privileges are required to access this resource.",
                "danger",
            )
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


def student_required(f):
    """Decorator to restrict view access to authenticated students only."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in as a student to access this page.", "warning")
            return redirect(url_for("auth.login", next=request.url))
        if not current_user.is_student_member:
            flash(
                "Access restricted: This action is designated for student accounts.",
                "warning",
            )
            abort(403)
        return f(*args, **kwargs)

    return decorated_function
