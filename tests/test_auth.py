from flask import url_for


def test_login_required(client):
    """Test that the @login_required decorator redirects to the login page."""
    response = client.get(url_for("main.create_liquor"))
    assert response.status_code == 302
    assert "/login" in response.location
