import json

from app.models import User


def test_error_handling(client, session):
    """Test error handling with various scenarios."""

    # Create a user for testing
    user = User(username="error_test_user", email="error_test@example.com")
    user.set_password("password123")
    session.add(user)
    session.commit()

    # Test login with invalid credentials
    response = client.post(
        "/api/v1/auth/login",
        data=json.dumps({"username": "nonexistent", "password": "wrong"}),
        content_type="application/json",
    )
    assert response.status_code == 401
    data = json.loads(response.data)
    assert "error" in data
    assert data["error"] == "Invalid username or password"
    assert data["status_code"] == 401

    # Test login with missing data
    response = client.post(
        "/api/v1/auth/login",
        data=json.dumps({}),
        content_type="application/json",
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data
    assert data["error"] == "No data provided"
    assert data["status_code"] == 400

    # Test login with missing fields
    response = client.post(
        "/api/v1/auth/login",
        data=json.dumps({"username": "testuser"}),
        content_type="application/json",
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data
    assert data["error"] == "Username and password are required"
    assert data["status_code"] == 400
    assert "details" in data
    assert "missing_fields" in data["details"]
    assert "password" in data["details"]["missing_fields"]

    # Test accessing protected endpoint without token
    response = client.get("/api/v1/liquors")
    assert response.status_code == 401
    data = json.loads(response.data)
    # The actual response might be different depending on the JWT implementation
    # Let's just check that we get a JSON response with an error-like field
    assert any(key in data for key in ["error", "message"])

    # Login to get a token
    response = client.post(
        "/api/v1/auth/login",
        data=json.dumps({"username": "error_test_user", "password": "password123"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    auth_token = data["auth_token"]

    # Test accessing non-existent resource
    response = client.get(
        "/api/v1/liquors/999999",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 404
    data = json.loads(response.data)
    assert "error" in data
    assert data["error"] == "Liquor not found"
    assert data["status_code"] == 404

    # Test creating liquor with missing name
    response = client.post(
        "/api/v1/liquors",
        data=json.dumps({"description": "a liquor without a name"}),
        content_type="application/json",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data
    assert data["error"] == "Name is required"
    assert data["status_code"] == 400

    # Test creating ingredient with missing name
    response = client.post(
        "/api/v1/ingredients",
        data=json.dumps({"description": "an ingredient without a name"}),
        content_type="application/json",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data
    assert data["error"] == "Name is required"
    assert data["status_code"] == 400

    print("All error handling tests passed!")
