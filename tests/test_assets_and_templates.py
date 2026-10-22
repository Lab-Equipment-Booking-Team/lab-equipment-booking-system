from tests.conftest import login_client


def test_static_css_and_js_files_served_successfully(client):
    """Test that static CSS and JavaScript files are correctly served with 200 OK."""
    # Test CSS
    css_resp = client.get("/static/css/style.css")
    assert css_resp.status_code == 200
    assert "text/css" in css_resp.content_type
    assert b"--navy-primary" in css_resp.data

    # Test script.js
    js_resp = client.get("/static/js/script.js")
    assert js_resp.status_code == 200
    assert "javascript" in js_resp.content_type
    assert b"DOMContentLoaded" in js_resp.data

    # Test main.js compatibility
    main_js_resp = client.get("/static/js/main.js")
    assert main_js_resp.status_code == 200
    assert "javascript" in main_js_resp.content_type
    assert b"DOMContentLoaded" in main_js_resp.data


def test_public_pages_link_css_and_js_correctly(client, sample_equipment):
    """Test that public templates (landing, about, login, register, catalogue, detail) link CSS and JS via url_for."""
    public_urls = [
        "/",
        "/about",
        "/auth/login",
        "/auth/register",
        "/equipment",
        f"/equipment/{sample_equipment.id}",
    ]

    for url in public_urls:
        resp = client.get(url)
        assert resp.status_code == 200, f"Failed on {url}"
        # Verify custom style.css is linked
        assert b'href="/static/css/style.css"' in resp.data, f"Missing style.css link on {url}"
        # Verify custom script.js is linked
        assert b'src="/static/js/script.js"' in resp.data, f"Missing script.js link on {url}"
        # Verify Bootstrap 5 CSS & JS are present
        assert b"bootstrap.min.css" in resp.data, f"Missing Bootstrap CSS on {url}"
        assert b"bootstrap.bundle.min.js" in resp.data, f"Missing Bootstrap JS on {url}"


def test_student_pages_link_css_and_js_correctly(client, student_user):
    """Test that protected student templates link CSS and JS correctly."""
    login_client(client, student_user.username, "StudentSecret123!")

    student_urls = [
        "/student/dashboard",
        "/student/book",
        "/student/my-bookings",
    ]

    for url in student_urls:
        resp = client.get(url)
        assert resp.status_code == 200, f"Failed on {url}"
        assert b'href="/static/css/style.css"' in resp.data, f"Missing style.css link on {url}"
        assert b'src="/static/js/script.js"' in resp.data, f"Missing script.js link on {url}"
        assert b"bootstrap.min.css" in resp.data
        assert b"bootstrap.bundle.min.js" in resp.data


def test_staff_pages_link_css_and_js_correctly(client, staff_user, sample_equipment):
    """Test that protected staff templates link CSS and JS correctly."""
    login_client(client, staff_user.username, "StaffSecret123!")

    staff_urls = [
        "/staff/dashboard",
        "/staff/requests/pending",
        "/staff/equipment",
        "/staff/equipment/new",
        f"/staff/equipment/{sample_equipment.id}/edit",
        "/staff/bookings/history",
    ]

    for url in staff_urls:
        resp = client.get(url)
        assert resp.status_code == 200, f"Failed on {url}"
        assert b'href="/static/css/style.css"' in resp.data, f"Missing style.css link on {url}"
        assert b'src="/static/js/script.js"' in resp.data, f"Missing script.js link on {url}"
        assert b"bootstrap.min.css" in resp.data
        assert b"bootstrap.bundle.min.js" in resp.data


def test_error_pages_link_css_and_js_correctly(client):
    """Test that error pages (404, 403) correctly link CSS and JS."""
    # 404 Page
    resp_404 = client.get("/nonexistent-page-xyz")
    assert resp_404.status_code == 404
    assert b'href="/static/css/style.css"' in resp_404.data
    assert b'src="/static/js/script.js"' in resp_404.data
