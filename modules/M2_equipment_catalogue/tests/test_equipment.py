from datetime import date, time

from database.database import db
from modules.M3_booking_form_model.models import Booking, Equipment
from tests.conftest import login_client


def test_catalogue_public_access(client, sample_equipment):
    """Test that equipment catalogue is accessible to all users."""
    response = client.get("/equipment")
    assert response.status_code == 200
    assert sample_equipment.name.encode() in response.data
    assert sample_equipment.code.encode() in response.data


def test_catalogue_search_and_filter(client, sample_equipment, maintenance_equipment):
    """Test searching by keyword and filtering by category/status."""
    # Search by keyword
    resp_search = client.get("/equipment?q=Fluorescence")
    assert resp_search.status_code == 200
    assert sample_equipment.name.encode() in resp_search.data
    assert maintenance_equipment.name.encode() not in resp_search.data

    # Filter by category
    resp_cat = client.get("/equipment?category=Centrifuges+%26+Separation")
    assert resp_cat.status_code == 200
    assert maintenance_equipment.name.encode() in resp_cat.data
    assert sample_equipment.name.encode() not in resp_cat.data

    # Filter by status
    resp_status = client.get("/equipment?status=Under+Maintenance")
    assert resp_status.status_code == 200
    assert maintenance_equipment.name.encode() in resp_status.data
    assert sample_equipment.name.encode() not in resp_status.data


def test_equipment_detail_view(client, sample_equipment):
    """Test viewing detailed specifications for a piece of equipment."""
    response = client.get(f"/equipment/{sample_equipment.id}")
    assert response.status_code == 200
    assert sample_equipment.name.encode() in response.data
    assert sample_equipment.code.encode() in response.data
    assert b"Microscopes" in response.data


def test_staff_add_equipment_success(client, staff_user):
    """Test staff successfully adding new equipment."""
    login_client(client, staff_user.username, "StaffSecret123!")

    response = client.post(
        "/staff/equipment/new",
        data={
            "code": "EQ-NEW-01",
            "name": "New Laser Profilometer",
            "category": "Electronics & Measurement",
            "description": "Surface topology measurement unit",
            "quantity_available": 2,
            "status": "Available",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"added successfully" in response.data

    item = Equipment.query.filter_by(code="EQ-NEW-01").first()
    assert item is not None
    assert item.name == "New Laser Profilometer"
    assert item.quantity_available == 2


def test_staff_add_equipment_validation_failure(client, staff_user, sample_equipment):
    """Test server-side validation rejecting duplicate code or invalid quantity."""
    login_client(client, staff_user.username, "StaffSecret123!")

    # Duplicate code
    resp1 = client.post(
        "/staff/equipment/new",
        data={
            "code": sample_equipment.code,  # Duplicate!
            "name": "Another Microscope",
            "category": "Microscopes",
            "quantity_available": 1,
            "status": "Available",
        },
        follow_redirects=True,
    )
    assert b"already registered" in resp1.data

    # Negative quantity
    resp2 = client.post(
        "/staff/equipment/new",
        data={
            "code": "EQ-INV-QTY",
            "name": "Invalid Qty Equipment",
            "category": "Microscopes",
            "quantity_available": -5,
            "status": "Available",
        },
        follow_redirects=True,
    )
    assert b"must be at least 1" in resp2.data


def test_staff_edit_equipment(client, staff_user, sample_equipment):
    """Test staff updating equipment details."""
    login_client(client, staff_user.username, "StaffSecret123!")

    response = client.post(
        f"/staff/equipment/{sample_equipment.id}/edit",
        data={
            "code": sample_equipment.code,
            "name": "Updated Microscope Name",
            "category": sample_equipment.category,
            "description": "Updated specifications description",
            "quantity_available": 5,
            "status": "Under Maintenance",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"updated successfully" in response.data

    db.session.refresh(sample_equipment)
    assert sample_equipment.name == "Updated Microscope Name"
    assert sample_equipment.quantity_available == 5
    assert sample_equipment.status == "Under Maintenance"


def test_staff_delete_equipment_without_bookings(client, staff_user):
    """Test that equipment without any booking records can be deleted."""
    # Create unbooked equipment
    unbooked = Equipment(
        code="EQ-TEMP-DEL",
        name="Temporary Equipment",
        category="General Laboratory Equipment",
        quantity_available=1,
        status="Available",
    )
    db.session.add(unbooked)
    db.session.commit()
    eq_id = unbooked.id

    login_client(client, staff_user.username, "StaffSecret123!")
    response = client.post(
        f"/staff/equipment/{eq_id}/delete",
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"deleted successfully" in response.data
    assert db.session.get(Equipment, eq_id) is None


def test_prevent_equipment_deletion_with_existing_bookings(
    client, staff_user, student_user, sample_equipment
):
    """Ensure equipment CANNOT be deleted if historical or active booking records exist."""
    # Add a booking referencing this equipment
    booking = Booking(
        user_id=student_user.id,
        equipment_id=sample_equipment.id,
        booking_date=date(2026, 11, 1),
        start_time=time(10, 0),
        end_time=time(12, 0),
        quantity=1,
        purpose="Important thesis research experiment",
        status=Booking.STATUS_APPROVED,
    )
    db.session.add(booking)
    db.session.commit()

    login_client(client, staff_user.username, "StaffSecret123!")
    response = client.post(
        f"/staff/equipment/{sample_equipment.id}/delete",
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Cannot delete" in response.data
    assert b"booking record(s) reference this equipment" in response.data

    # Verify equipment still exists in database
    assert db.session.get(Equipment, sample_equipment.id) is not None


def test_student_cannot_add_or_delete_equipment(client, student_user, sample_equipment):
    """Test student role is forbidden from adding, editing, or deleting equipment."""
    login_client(client, student_user.username, "StudentSecret123!")

    # Student cannot access add equipment
    resp_add = client.get("/staff/equipment/new")
    assert resp_add.status_code == 403

    # Student cannot post to add equipment
    resp_post_add = client.post("/staff/equipment/new", data={})
    assert resp_post_add.status_code == 403

    # Student cannot delete equipment
    resp_del = client.post(f"/staff/equipment/{sample_equipment.id}/delete")
    assert resp_del.status_code == 403
