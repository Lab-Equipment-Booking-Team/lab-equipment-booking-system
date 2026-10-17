from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user

from models import Equipment

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Public landing page featuring equipment overview and quick portals."""
    total_equipment = Equipment.query.count()
    available_equipment = Equipment.query.filter_by(
        status=Equipment.STATUS_AVAILABLE
    ).count()
    categories = [
        c[0]
        for c in Equipment.query.with_entities(Equipment.category)
        .distinct()
        .all()
    ]
    featured_equipment = (
        Equipment.query.filter_by(status=Equipment.STATUS_AVAILABLE)
        .limit(6)
        .all()
    )

    return render_template(
        "index.html",
        total_equipment=total_equipment,
        available_equipment=available_equipment,
        categories=categories,
        featured_equipment=featured_equipment,
    )


@main_bp.route("/about")
def about():
    """About laboratory system, objectives, features, and workflow guide."""
    return render_template("about.html")


@main_bp.route("/dashboard")
def dashboard():
    """Convenience redirect to user's role-specific dashboard."""
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))
    if current_user.is_staff_member:
        return redirect(url_for("staff.dashboard"))
    return redirect(url_for("student.dashboard"))
