import pytest

from app import db
from app.models import Equipment


def test_equipment_creation_and_fields(app):
    """FR-01: Equipment item contains name, category, and status."""
    with app.app_context():
        eq = Equipment(name="Rigol Oscilloscope", category="Electronics", status="Available")
        db.session.add(eq)
        db.session.commit()

        saved = Equipment.query.filter_by(name="Rigol Oscilloscope").first()
        assert saved is not None
        assert saved.name == "Rigol Oscilloscope"
        assert saved.category == "Electronics"
        assert saved.status == "Available"


def test_view_equipment_catalogue(client, app):
    """FR-01: All users can view the equipment list in catalogue."""
    with app.app_context():
        eq = Equipment(name="Ultimaker 3D Printer", category="Fabrication", status="Available")
        db.session.add(eq)
        db.session.commit()

    response = client.get("/equipment")
    assert response.status_code == 200
    assert b"Ultimaker 3D Printer" in response.data


def test_equipment_status_out_of_service(app):
    """FR-01: Equipment status can be set to 'Out of service'."""
    with app.app_context():
        eq = Equipment(name="Broken Microscope", category="Optics", status="Out of service")
        db.session.add(eq)
        db.session.commit()

        saved = Equipment.query.filter_by(name="Broken Microscope").first()
        assert saved is not None
        assert saved.status == "Out of service"