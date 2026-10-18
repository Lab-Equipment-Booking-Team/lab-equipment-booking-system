"""Authentication routing endpoints for Lab Equipment Booking System.

Assigned to: Module M1 – Accounts & Authentication
Member: Prabhashi Peiris (Student ID: 6308, GitHub: asp2023155)

Routes:
- GET, POST /auth/register: Student & Staff user registration
- GET, POST /auth/login: Role-based user login
- GET, POST /auth/logout: User session termination
"""

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user

from modules.M1_accounts_auth.service import (
    authenticate_user,
    is_safe_redirect_url,
    register_user,
)
from modules.M3_booking_form_model.models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth", template_folder="templates")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user account.

    Public registration defaults to Student role.
    Staff accounts require a verified Staff Registration Key.
    """
    if current_user.is_authenticated:
        if current_user.is_staff_member:
            return redirect(url_for("staff.dashboard"))
        return redirect(url_for("student.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        full_name = request.form.get("full_name", "").strip()
        student_or_staff_id = request.form.get("student_or_staff_id", "").strip().upper()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        staff_key = request.form.get("staff_key", "").strip()

        configured_key = current_app.config.get("STAFF_REGISTRATION_KEY")

        new_user, error_msg = register_user(
            username=username,
            email=email,
            full_name=full_name,
            student_or_staff_id=student_or_staff_id,
            password=password,
            confirm_password=confirm_password,
            staff_key=staff_key,
            configured_staff_key=configured_key,
        )

        if error_msg:
            flash(error_msg, "danger")
            return render_template("auth/register.html")

        role_label = "Staff" if new_user.role == User.ROLE_STAFF else "Student"
        flash(f"Account successfully created as {role_label}! You may now log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Log in existing users with role-based dashboard redirection."""
    if current_user.is_authenticated:
        if current_user.is_staff_member:
            return redirect(url_for("staff.dashboard"))
        return redirect(url_for("student.dashboard"))

    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))

        user, error_msg = authenticate_user(identifier, password)
        if error_msg:
            flash(error_msg, "warning" if "both" in error_msg else "danger")
            return render_template("auth/login.html")

        login_user(user, remember=remember)
        flash(f"Welcome back, {user.full_name}!", "success")

        next_page = request.args.get("next")
        if next_page and is_safe_redirect_url(next_page, request.host_url):
            return redirect(next_page)

        if user.is_staff_member:
            return redirect(url_for("staff.dashboard"))
        return redirect(url_for("student.dashboard"))

    return render_template("auth/login.html")


@auth_bp.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    """Log out the current user session."""
    logout_user()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("auth.login"))
