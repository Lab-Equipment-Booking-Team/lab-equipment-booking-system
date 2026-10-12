from models import Booking, Equipment, User
from tests.conftest import login_client


def test_cli_init_db(runner):
    """Test CLI init-db command."""
    result = runner.invoke(args=["init-db"])
    assert result.exit_code == 0
    assert "Initialized database tables successfully." in result.output


def test_cli_create_staff(runner, app):
    """Test CLI create-staff command creates an administrative user."""
    result = runner.invoke(
        args=[
            "create-staff",
            "--username",
            "cli_staff_user",
            "--email",
            "clistaff@university.edu",
            "--name",
            "Prof. Charles Darwin",
            "--staff-id",
            "STF-7001",
            "--password",
            "CliStaffPass123!",
        ]
    )
    assert result.exit_code == 0
    assert "Staff account 'cli_staff_user' successfully created!" in result.output

    with app.app_context():
        user = User.query.filter_by(username="cli_staff_user").first()
        assert user is not None
        assert user.role == User.ROLE_STAFF
        assert user.check_password("CliStaffPass123!") is True


def test_cli_seed_data(runner, app):
    """Test CLI seed-data command populates demo records."""
    result = runner.invoke(args=["seed-data"])
    assert result.exit_code == 0
    assert "Database successfully seeded" in result.output

    with app.app_context():
        assert Equipment.query.count() >= 6
        assert User.query.filter_by(username="staff_admin").first() is not None
        assert User.query.filter_by(username="student_alex").first() is not None
        assert Booking.query.count() >= 1


def test_main_routes_and_dashboard_redirection(
    client, student_user, staff_user
):
    """Test public landing page, about page, and convenience dashboard redirect."""
    # Landing page
    res_home = client.get("/")
    assert res_home.status_code == 200
    assert b"University Laboratory Equipment Booking System" in res_home.data

    # About page
    res_about = client.get("/about")
    assert res_about.status_code == 200
    assert b"Pawani" in res_about.data
    assert b"Prabhashi" in res_about.data
    assert b"Shashinika" in res_about.data
    assert b"Imasha" in res_about.data
    assert b"Hashini" in res_about.data

    # Unauthenticated dashboard redirect -> /auth/login
    res_dash_anon = client.get("/dashboard", follow_redirects=False)
    assert res_dash_anon.status_code == 302
    assert "/auth/login" in res_dash_anon.headers["Location"]

    # Student dashboard redirect
    login_client(client, student_user.username, "StudentSecret123!")
    res_dash_stu = client.get("/dashboard", follow_redirects=False)
    assert res_dash_stu.status_code == 302
    assert "/student/dashboard" in res_dash_stu.headers["Location"]
    client.get("/auth/logout")

    # Staff dashboard redirect
    login_client(client, staff_user.username, "StaffSecret123!")
    res_dash_stf = client.get("/dashboard", follow_redirects=False)
    assert res_dash_stf.status_code == 302
    assert "/staff/dashboard" in res_dash_stf.headers["Location"]


def test_api_check_availability(client, sample_equipment):
    """Test the JSON API endpoint for real-time equipment availability checks."""
    # Valid query
    resp = client.get(
        f"/equipment/api/check-availability?equipment_id={sample_equipment.id}&date=2026-11-15&start_time=10:00&end_time=12:00"
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert data["available_quantity"] == sample_equipment.quantity_available

    # Missing parameters
    resp_bad = client.get("/equipment/api/check-availability")
    assert resp_bad.status_code == 400

    # Inverted time range
    resp_inv = client.get(
        f"/equipment/api/check-availability?equipment_id={sample_equipment.id}&date=2026-11-15&start_time=14:00&end_time=10:00"
    )
    assert resp_inv.status_code == 400


def test_staff_booking_history_view_and_filters(
    client, staff_user, student_user, sample_equipment
):
    """Test staff viewing complete booking history and applying filters."""
    login_client(client, staff_user.username, "StaffSecret123!")

    # View history page
    resp = client.get("/staff/bookings/history")
    assert resp.status_code == 200
    assert b"Laboratory Reservation Archive" in resp.data

    # Filter by status and equipment
    resp_filter = client.get(
        f"/staff/bookings/history?status=Approved&equipment_id={sample_equipment.id}"
    )
    assert resp_filter.status_code == 200


def test_404_error_page(client):
    """Test custom 404 page for nonexistent routes."""
    resp = client.get("/this-route-does-not-exist-in-app")
    assert resp.status_code == 404
    assert b"Page Not Found" in resp.data
