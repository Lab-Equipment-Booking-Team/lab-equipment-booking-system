import pytest

from app import create_app
from config import TestingConfig
from models import Equipment, User, db


@pytest.fixture
def app():
    """Create and configure a Flask application instance for testing."""
    app = create_app(TestingConfig)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


@pytest.fixture
def client(app):
    """A test client for making HTTP requests."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for CLI commands."""
    return app.test_cli_runner()


@pytest.fixture
def student_user(app):
    """Create a verified test student."""
    user = User(
        username="student_john",
        email="john@student.university.edu",
        full_name="John Doe",
        student_or_staff_id="STU-2024-101",
        role=User.ROLE_STUDENT,
    )
    user.set_password("StudentSecret123!")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def student_user_two(app):
    """Create a second verified test student."""
    user = User(
        username="student_alice",
        email="alice@student.university.edu",
        full_name="Alice Smith",
        student_or_staff_id="STU-2024-102",
        role=User.ROLE_STUDENT,
    )
    user.set_password("StudentSecret123!")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def staff_user(app):
    """Create a verified test staff member."""
    user = User(
        username="staff_dr_smith",
        email="dr.smith@university.edu",
        full_name="Dr. Elizabeth Smith",
        student_or_staff_id="STF-9901",
        role=User.ROLE_STAFF,
    )
    user.set_password("StaffSecret123!")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def sample_equipment(app):
    """Create sample multi-unit laboratory equipment."""
    eq = Equipment(
        code="EQ-MIC-TEST",
        name="Test Fluorescence Microscope",
        category="Microscopes",
        description="High precision optical microscope for test environment",
        quantity_available=3,
        status=Equipment.STATUS_AVAILABLE,
    )
    db.session.add(eq)
    db.session.commit()
    return eq


@pytest.fixture
def single_unit_equipment(app):
    """Create single-unit scarce laboratory equipment."""
    eq = Equipment(
        code="EQ-NMR-SINGLE",
        name="Single Unit NMR Spectrometer",
        category="Spectrometry & Optical",
        description="Exclusive single-unit spectrometer",
        quantity_available=1,
        status=Equipment.STATUS_AVAILABLE,
    )
    db.session.add(eq)
    db.session.commit()
    return eq


@pytest.fixture
def maintenance_equipment(app):
    """Create equipment currently under maintenance."""
    eq = Equipment(
        code="EQ-MAINT-01",
        name="Broken Centrifuge",
        category="Centrifuges & Separation",
        description="Currently offline for rotor recalibration",
        quantity_available=2,
        status=Equipment.STATUS_MAINTENANCE,
    )
    db.session.add(eq)
    db.session.commit()
    return eq


def login_client(client, username, password):
    """Helper function to log in a user with the test client."""
    return client.post(
        "/auth/login",
        data={"identifier": username, "password": password},
        follow_redirects=True,
    )
