from app import db
from app.models import Equipment, User


def test_view_equipment_catalogue_and_filter(client, app):
    """FR-01: Logged-in/guest users can view and filter equipment by category."""
    with app.app_context():
        eq1 = Equipment(name="Rigol Oscilloscope", category="Electronics", status="Available")
        eq2 = Equipment(name="Ultimaker 3D Printer", category="Fabrication", status="Available")
        db.session.add_all([eq1, eq2])
        db.session.commit()

    # 1. View all equipment
    res_all = client.get("/equipment")
    assert res_all.status_code == 200
    assert b"Rigol Oscilloscope" in res_all.data
    assert b"Ultimaker 3D Printer" in res_all.data

    # 2. Filter by category Electronics
    res_filter = client.get("/equipment?category=Electronics")
    assert res_filter.status_code == 200
    assert b"Rigol Oscilloscope" in res_filter.data
    assert b"Ultimaker 3D Printer" not in res_filter.data

    # 3. Search keyword
    res_search = client.get("/equipment?q=Ultimaker")
    assert res_search.status_code == 200
    assert b"Ultimaker 3D Printer" in res_search.data
    assert b"Rigol Oscilloscope" not in res_search.data


def test_staff_can_add_edit_delete_equipment(client, app):
    """FR-01: Staff can add, edit, and delete equipment."""
    with app.app_context():
        staff = User(username="staff_mgr", email="staffmgr@rusl.ac.lk", role="Staff")
        staff.set_password("StaffPass123!")
        db.session.add(staff)
        db.session.commit()

    # Log in as Staff
    client.post(
        "/login",
        data={"identifier": "staff_mgr", "password": "StaffPass123!"},
        follow_redirects=True,
    )

    # 1. Add Equipment
    res_add = client.post(
        "/equipment/add",
        data={
            "name": "Raspberry Pi 5",
            "category": "Computing",
            "description": "Latest Pi board with PCIe support",
            "status": "Available",
        },
        follow_redirects=True,
    )
    assert res_add.status_code == 200
    assert b"added successfully" in res_add.data

    with app.app_context():
        item = Equipment.query.filter_by(name="Raspberry Pi 5").first()
        assert item is not None
        assert item.category == "Computing"
        item_id = item.id

    # 2. Edit Equipment
    res_edit = client.post(
        f"/equipment/{item_id}/edit",
        data={
            "name": "Raspberry Pi 5 Pro",
            "category": "Computing",
            "description": "Updated description",
            "status": "Out of service",
        },
        follow_redirects=True,
    )
    assert res_edit.status_code == 200
    assert b"updated successfully" in res_edit.data

    with app.app_context():
        updated_item = Equipment.query.get(item_id)
        assert updated_item.name == "Raspberry Pi 5 Pro"
        assert updated_item.status == "Out of service"

    # 3. Delete Equipment
    res_del = client.post(
        f"/equipment/{item_id}/delete",
        follow_redirects=True,
    )
    assert res_del.status_code == 200
    assert b"removed from catalogue" in res_del.data


def test_student_cannot_add_equipment(client, app):
    """FR-01: Students cannot add equipment."""
    with app.app_context():
        student = User(username="student_regular", email="reg@rusl.ac.lk", role="Student")
        student.set_password("Pass123!")
        db.session.add(student)
        db.session.commit()

    # Login as student
    client.post(
        "/login",
        data={"identifier": "student_regular", "password": "Pass123!"},
        follow_redirects=True,
    )

    # Attempt to post to add equipment
    res = client.post(
        "/equipment/add",
        data={
            "name": "Unauthorized Laser",
            "category": "Optics",
            "description": "Unauthorized item",
            "status": "Available",
        },
        follow_redirects=True,
    )
    assert b"Access denied: Staff privileges are required" in res.data