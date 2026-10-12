from models import User
from tests.conftest import login_client


def test_student_registration_success(client):
    """Test successful student registration through public portal."""
    response = client.post(
        "/auth/register",
        data={
            "full_name": "New Student",
            "student_or_staff_id": "STU-9999",
            "username": "new_student",
            "email": "new.student@university.edu",
            "password": "Password123!",
            "confirm_password": "Password123!",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Account successfully created as Student" in response.data

    user = User.query.filter_by(username="new_student").first()
    assert user is not None
    assert user.role == User.ROLE_STUDENT
    assert user.is_student_member is True
    assert user.is_staff_member is False
    assert user.check_password("Password123!") is True
    assert user.password_hash != "Password123!"  # Passwords must be hashed!


def test_registration_password_mismatch(client):
    """Test that mismatched passwords fail registration with an error."""
    response = client.post(
        "/auth/register",
        data={
            "full_name": "Test Mismatch",
            "student_or_staff_id": "STU-001",
            "username": "mismatch_user",
            "email": "mismatch@university.edu",
            "password": "Password123!",
            "confirm_password": "DifferentPassword456!",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Passwords do not match" in response.data
    assert User.query.filter_by(username="mismatch_user").first() is None


def test_registration_duplicate_username_and_email(client, student_user):
    """Test that duplicate usernames or emails are rejected."""
    # Duplicate username
    response = client.post(
        "/auth/register",
        data={
            "full_name": "Duplicate User",
            "student_or_staff_id": "STU-002",
            "username": student_user.username,
            "email": "unique@university.edu",
            "password": "Password123!",
            "confirm_password": "Password123!",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"already in use" in response.data

    # Duplicate email
    response2 = client.post(
        "/auth/register",
        data={
            "full_name": "Duplicate Email User",
            "student_or_staff_id": "STU-003",
            "username": "unique_username",
            "email": student_user.email,
            "password": "Password123!",
            "confirm_password": "Password123!",
        },
        follow_redirects=True,
    )
    assert response2.status_code == 200
    assert b"already registered" in response2.data


def test_public_registration_cannot_self_grant_staff(client):
    """Ensure public registration without valid key cannot grant Staff role."""
    # Without staff key
    client.post(
        "/auth/register",
        data={
            "full_name": "Attempted Staff",
            "student_or_staff_id": "STF-FAKE",
            "username": "attempted_staff",
            "email": "fake.staff@university.edu",
            "password": "Password123!",
            "confirm_password": "Password123!",
            "staff_key": "",
        },
        follow_redirects=True,
    )
    user = User.query.filter_by(username="attempted_staff").first()
    assert user.role == User.ROLE_STUDENT

    # With invalid staff key
    response = client.post(
        "/auth/register",
        data={
            "full_name": "Invalid Key Staff",
            "student_or_staff_id": "STF-FAKE2",
            "username": "invalid_key_staff",
            "email": "invalid.staff@university.edu",
            "password": "Password123!",
            "confirm_password": "Password123!",
            "staff_key": "WRONG_SECRET_KEY",
        },
        follow_redirects=True,
    )
    assert b"Invalid Staff Registration Key" in response.data
    assert User.query.filter_by(username="invalid_key_staff").first() is None


def test_authorized_staff_registration_with_key(client, app):
    """Test that registration with valid authorized key creates a Staff account."""
    staff_key = app.config.get("STAFF_REGISTRATION_KEY", "LAB-STAFF-AUTH-2026")
    response = client.post(
        "/auth/register",
        data={
            "full_name": "Authorized Staff",
            "student_or_staff_id": "STF-8888",
            "username": "auth_staff_member",
            "email": "auth.staff@university.edu",
            "password": "StaffPassword123!",
            "confirm_password": "StaffPassword123!",
            "staff_key": staff_key,
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Account successfully created as Staff" in response.data

    user = User.query.filter_by(username="auth_staff_member").first()
    assert user is not None
    assert user.role == User.ROLE_STAFF
    assert user.is_staff_member is True


def test_successful_student_login(client, student_user):
    """Test successful student login and redirect to student dashboard."""
    response = login_client(client, student_user.username, "StudentSecret123!")
    assert response.status_code == 200
    assert b"Welcome back, John Doe!" in response.data
    assert b"Student Dashboard" in response.data


def test_successful_staff_login(client, staff_user):
    """Test successful staff login and redirect to staff dashboard."""
    response = login_client(client, staff_user.username, "StaffSecret123!")
    assert response.status_code == 200
    assert b"Laboratory Staff Dashboard" in response.data


def test_invalid_login_credentials(client, student_user):
    """Test login failure with incorrect password and non-existent username."""
    # Wrong password
    response = login_client(client, student_user.username, "IncorrectPass!")
    assert response.status_code == 200
    assert b"Invalid credentials" in response.data

    # Non-existent username
    response2 = login_client(client, "nonexistent_user", "AnyPassword123!")
    assert response2.status_code == 200
    assert b"Invalid credentials" in response2.data

    # Blank submission
    response3 = client.post(
        "/auth/login", data={"identifier": "", "password": ""}, follow_redirects=True
    )
    assert b"Please enter both" in response3.data


def test_logout(client, student_user):
    """Test user logout successfully ends session."""
    login_client(client, student_user.username, "StudentSecret123!")
    response = client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"You have been logged out successfully." in response.data


def test_unauthenticated_access_redirection(client):
    """Test that protected student and staff routes redirect unauthenticated users to login."""
    # Student dashboard
    resp1 = client.get("/student/dashboard", follow_redirects=False)
    assert resp1.status_code == 302
    assert "/auth/login" in resp1.headers["Location"]

    # Staff dashboard
    resp2 = client.get("/staff/dashboard", follow_redirects=False)
    assert resp2.status_code == 302
    assert "/auth/login" in resp2.headers["Location"]


def test_student_forbidden_from_staff_routes(client, student_user):
    """Test that a logged-in student receives 403 Forbidden when accessing staff routes."""
    login_client(client, student_user.username, "StudentSecret123!")

    # Attempt accessing staff dashboard
    resp = client.get("/staff/dashboard")
    assert resp.status_code == 403
    assert b"Access Denied: Insufficient Privileges" in resp.data

    # Attempt accessing staff pending requests
    resp2 = client.get("/staff/requests/pending")
    assert resp2.status_code == 403

    # Attempt accessing equipment management
    resp3 = client.get("/staff/equipment")
    assert resp3.status_code == 403
