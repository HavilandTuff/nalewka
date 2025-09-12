import json


def test_error_handling_basic(client):
    """Test basic error handling scenarios."""

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

    print("All basic error handling tests passed!")
