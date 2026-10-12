import re
from urllib.parse import urlsplit

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
from sqlalchemy.exc import SQLAlchemyError

from models import User, db

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def is_safe_url(target: str) -> bool:
    """Ensure redirect URL belongs to local application to prevent open redirects."""
    if not target:
        return False
    ref_url = urlsplit(request.host_url)
    test_url = urlsplit(target)
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc or not test_url.netloc


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user account.
    By default, public registration creates Student accounts only.
    Staff accounts require an authorized staff registration key.
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

        # Input validations
        if not username or not email or not full_name or not student_or_staff_id or not password:
            flash("All required fields must be completed.", "danger")
            return render_template("auth/register.html")

        if len(username) < 3 or len(username) > 30:
            flash("Username must be between 3 and 30 characters long.", "danger")
            return render_template("auth/register.html")

        if not re.match(r"^[a-zA-Z0-9_.-]+$", username):
            flash("Username may only contain letters, numbers, dots, and underscores.", "danger")
            return render_template("auth/register.html")

        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
            flash("Please enter a valid email address.", "danger")
            return render_template("auth/register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template("auth/register.html")

        if password != confirm_password:
            flash("Passwords do not match. Please verify and try again.", "danger")
            return render_template("auth/register.html")

        # Check existing user
        if User.query.filter_by(username=username).first():
            flash(f"The username '{username}' is already in use. Please choose another.", "danger")
            return render_template("auth/register.html")

        if User.query.filter_by(email=email).first():
            flash(f"The email address '{email}' is already registered.", "danger")
            return render_template("auth/register.html")

        # Determine role: Public registration is always student, unless authorized staff key is provided
        assigned_role = User.ROLE_STUDENT
        if staff_key:
            configured_key = current_app.config.get("STAFF_REGISTRATION_KEY")
            if configured_key and staff_key == configured_key:
                assigned_role = User.ROLE_STAFF
            else:
                flash("Invalid Staff Registration Key. Staff account registration failed.", "danger")
                return render_template("auth/register.html")

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
            role_label = "Staff" if assigned_role == User.ROLE_STAFF else "Student"
            flash(f"Account successfully created as {role_label}! You may now log in.", "success")
            return redirect(url_for("auth.login"))
        except SQLAlchemyError:
            db.session.rollback()
            flash("An unexpected error occurred while saving the account. Please try again.", "danger")
            return render_template("auth/register.html")

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

        if not identifier or not password:
            flash("Please enter both username/email and your password.", "warning")
            return render_template("auth/login.html")

        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier.lower())
        ).first()

        if not user or not user.check_password(password):
            flash("Invalid credentials. Please verify your username and password.", "danger")
            return render_template("auth/login.html")

        login_user(user, remember=remember)
        flash(f"Welcome back, {user.full_name}!", "success")

        next_page = request.args.get("next")
        if next_page and is_safe_url(next_page):
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
    return redirect(url_for("main.index"))
