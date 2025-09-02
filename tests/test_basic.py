from typing import Any


def test_index_page_loads(client: Any) -> None:
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome to Nalewka" in response.data  # For logged-out user


def test_404_page(client: Any) -> None:
    """
    GIVEN a Flask application configured for testing
    WHEN a non-existent page is requested (GET)
    THEN check that a 404 error is returned
    """
    response = client.get("/a-page-that-does-not-exist")
    assert response.status_code == 404
    assert b"Page Not Found" in response.data
