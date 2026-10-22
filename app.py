"""Lab Equipment Booking System - Main Application Entry Point.

Central Flask application factory and CLI commands integrating all five modules:
- Module M1: Accounts & Authentication (Prabhashi Peiris)
- Module M2: Equipment Catalogue (Shashinika Rathnayaka)
- Module M3: Booking Form & Model (Imasha Chandralal)
- Module M4: Booking Validation & QA (Hashini Wickramasinghe)
- Module M5: Approval & Integration (Pawani Thathsarani Bandara)
"""

import os
from datetime import UTC, date, datetime, time

import click
import jinja2
from flask import Blueprint, Flask, redirect, render_template, url_for
from flask_login import LoginManager, current_user

from config import Config, config_by_name
from database.database import db
from modules.M1_accounts_auth.routes import auth_bp
from modules.M2_equipment_catalogue.routes import equipment_bp
from modules.M3_booking_form_model.models import Booking, Equipment, User
from modules.M3_booking_form_model.routes import bookings_bp
from modules.M5_approval_integration.routes import staff_bp

# Flask-Login session manager
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(user_id):
    """Load user object for Flask-Login session management."""
    return db.session.get(User, int(user_id))


# Main public routes blueprint (Home, About, Dashboard redirect)
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


def create_app(config_class=None):
    """Application factory for the Lab Equipment Booking System."""
    app = Flask(__name__)

    if config_class is None:
        env_mode = os.environ.get("FLASK_ENV", "development")
        config_class = config_by_name.get(env_mode, Config)

    app.config.from_object(config_class)

    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # Configure Jinja ChoiceLoader to discover templates across all modules and root
    template_paths = [
        os.path.join(app.root_path, "templates"),
        os.path.join(app.root_path, "modules", "M1_accounts_auth", "templates"),
        os.path.join(app.root_path, "modules", "M2_equipment_catalogue", "templates"),
        os.path.join(app.root_path, "modules", "M3_booking_form_model", "templates"),
        os.path.join(app.root_path, "modules", "M5_approval_integration", "templates"),
    ]
    app.jinja_loader = jinja2.ChoiceLoader([
        app.jinja_loader,
        jinja2.FileSystemLoader(template_paths),
    ])

    # Initialize extensions with central shared database
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints from integrated modules
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(equipment_bp)
    app.register_blueprint(bookings_bp)

    app.register_blueprint(staff_bp)

    # Register HTTP error handlers
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    # Global context processors for navigation badges and dynamic year
    @app.context_processor
    def inject_global_data():
        staff_pending_count = 0
        if current_user.is_authenticated and current_user.is_staff_member:
            staff_pending_count = Booking.query.filter_by(
                status=Booking.STATUS_PENDING
            ).count()
        return {
            "current_year": datetime.now(UTC).year,
            "staff_pending_count": staff_pending_count,
        }

    # Register CLI management commands
    register_commands(app)

    return app


def register_commands(app: Flask):
    """Register custom CLI management commands for database initialization and seeding."""

    @app.cli.command("init-db")
    def init_db_command():
        """Create all database tables."""
        db.create_all()
        click.echo("Initialized database tables successfully.")

    @app.cli.command("create-staff")
    @click.option("--username", prompt=True, help="Staff username")
    @click.option("--email", prompt=True, help="Staff email address")
    @click.option("--name", prompt=True, help="Staff full name")
    @click.option("--staff-id", prompt=True, help="Staff ID (e.g. STF-1001)")
    @click.password_option(prompt=True, confirmation_prompt=True, help="Staff password")
    def create_staff_command(username, email, name, staff_id, password):
        """Securely create a verified Staff administrator account via CLI."""
        if User.query.filter_by(username=username).first():
            click.echo(f"Error: Username '{username}' already exists.")
            return
        if User.query.filter_by(email=email).first():
            click.echo(f"Error: Email '{email}' already exists.")
            return

        staff_user = User(
            username=username.strip(),
            email=email.strip().lower(),
            full_name=name.strip(),
            student_or_staff_id=staff_id.strip().upper(),
            role=User.ROLE_STAFF,
        )
        staff_user.set_password(password)

        db.session.add(staff_user)
        db.session.commit()
        click.echo(f"Staff account '{username}' successfully created!")

    @app.cli.command("seed-data")
    def seed_data_command():
        """Seed sample laboratory equipment, staff, students, and demo bookings."""
        db.create_all()

        # Create demo staff
        staff = User.query.filter_by(username="staff_admin").first()
        if not staff:
            staff = User(
                username="staff_admin",
                email="admin@university.edu",
                full_name="Dr. Sarah Johnson (Lab Manager)",
                student_or_staff_id="STF-0101",
                role=User.ROLE_STAFF,
            )
            staff.set_password("StaffPass123!")
            db.session.add(staff)

        # Create demo student
        student = User.query.filter_by(username="student_alex").first()
        if not student:
            student = User(
                username="student_alex",
                email="alex.chen@student.university.edu",
                full_name="Alex Chen",
                student_or_staff_id="STU-2024-042",
                role=User.ROLE_STUDENT,
            )
            student.set_password("StudentPass123!")
            db.session.add(student)

        # Create secondary demo student
        student2 = User.query.filter_by(username="student_maya").first()
        if not student2:
            student2 = User(
                username="student_maya",
                email="maya.patel@student.university.edu",
                full_name="Maya Patel",
                student_or_staff_id="STU-2024-089",
                role=User.ROLE_STUDENT,
            )
            student2.set_password("StudentPass123!")
            db.session.add(student2)

        # Equipment catalogue initial data
        sample_equipment = [
            {
                "code": "EQ-MIC-01",
                "name": "Olympus BX53 Biological Fluorescence Microscope",
                "category": "Microscopes",
                "description": "High-magnification fluorescence microscope with motorized stage and digital image capture.",
                "quantity_available": 3,
                "status": Equipment.STATUS_AVAILABLE,
            },
            {
                "code": "EQ-SPEC-02",
                "name": "Shimadzu UV-1900i UV-Vis Spectrophotometer",
                "category": "Spectrometry & Optical",
                "description": "Double-beam UV-Vis spectrophotometer with ultra-fast wavelength scanning and touch screen interface.",
                "quantity_available": 2,
                "status": Equipment.STATUS_AVAILABLE,
            },
            {
                "code": "EQ-CENT-03",
                "name": "Eppendorf 5810R Refrigerated Centrifuge",
                "category": "Centrifuges & Separation",
                "description": "Refrigerated benchtop centrifuge capable of up to 14,000 RPM with swing-bucket and fixed-angle rotors.",
                "quantity_available": 4,
                "status": Equipment.STATUS_AVAILABLE,
            },
            {
                "code": "EQ-OSC-04",
                "name": "Tektronix TBS2000B Digital Storage Oscilloscope",
                "category": "Electronics & Measurement",
                "description": "4-channel 100 MHz digital storage oscilloscope with 2 GS/s sample rate and USB waveform export.",
                "quantity_available": 6,
                "status": Equipment.STATUS_AVAILABLE,
            },
            {
                "code": "EQ-HOT-05",
                "name": "Corning PC-420D Digital Stirring Hot Plate",
                "category": "Thermal & Heating",
                "description": "Microprocessor-controlled stirring hot plate with Pyroceram glass-ceramic top and temperature probe.",
                "quantity_available": 8,
                "status": Equipment.STATUS_AVAILABLE,
            },
            {
                "code": "EQ-PCR-06",
                "name": "Bio-Rad T100 Thermal Cycler PCR System",
                "category": "General Laboratory Equipment",
                "description": "96-well thermal cycler with intuitive touchscreen interface and gradient capability for DNA amplification.",
                "quantity_available": 2,
                "status": Equipment.STATUS_MAINTENANCE,
            },
        ]

        for eq_data in sample_equipment:
            if not Equipment.query.filter_by(code=eq_data["code"]).first():
                eq = Equipment(**eq_data)
                db.session.add(eq)

        db.session.commit()

        # Add sample booking if none exist
        if Booking.query.count() == 0 and student and Equipment.query.first():
            eq1 = Equipment.query.filter_by(code="EQ-MIC-01").first()
            if eq1:
                sample_b1 = Booking(
                    user_id=student.id,
                    equipment_id=eq1.id,
                    booking_date=date(2026, 10, 20),
                    start_time=time(10, 0),
                    end_time=time(12, 0),
                    quantity=1,
                    purpose="Cell morphology analysis for Molecular Biology FYP Project",
                    status=Booking.STATUS_APPROVED,
                    reviewed_by_id=staff.id,
                    reviewed_at=datetime.now(UTC).replace(tzinfo=None),
                )
                db.session.add(sample_b1)

                sample_b2 = Booking(
                    user_id=student.id,
                    equipment_id=eq1.id,
                    booking_date=date(2026, 10, 22),
                    start_time=time(14, 0),
                    end_time=time(16, 0),
                    quantity=1,
                    purpose="Follow-up staining verification protocol",
                    status=Booking.STATUS_PENDING,
                )
                db.session.add(sample_b2)
                db.session.commit()

        click.echo("Database successfully seeded with realistic sample data!")


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
