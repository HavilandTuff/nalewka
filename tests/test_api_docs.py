import json


def test_api_docs_endpoint(client):
    """Test that the API documentation endpoint returns the Swagger UI."""
    response = client.get("/api/v1/docs")
    assert response.status_code == 200
    assert b"swagger-ui" in response.data.lower()
    assert b"Nalewka API" in response.data


def test_api_root_endpoint(client):
    """Test that the API root endpoint returns the correct information."""
    response = client.get("/api/v1/")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "message" in data
    assert "version" in data
    assert "documentation" in data
    assert data["documentation"] == "/api/docs"
