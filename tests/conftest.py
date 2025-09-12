import os

import pytest

from app import create_app
from app import db as _db


@pytest.fixture(scope="session")
def app():
    """Create and configure a new app instance for each test session."""
    # Set testing environment variable
    os.environ["TESTING"] = "1"

    # Use in-memory SQLite database for testing
    app = create_app()
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False  # Disable CSRF for testing
    app.config["SERVER_NAME"] = "localhost.localdomain"  # For URL generation in tests

    # Establish an application context before running the tests
    with app.app_context():
        yield app

    # Clean up environment variable
    if "TESTING" in os.environ:
        del os.environ["TESTING"]


@pytest.fixture(scope="session")
def db(app):
    """Session-wide test database."""
    _db.app = app
    _db.create_all()

    yield _db

    # Don't drop all - let the in-memory database be destroyed when the app context ends
    # This is safer and ensures complete isolation


@pytest.fixture(scope="function")
def session(db):
    """
    Creates a new database session for a test.

    This fixture clears all data from the database before each test,
    ensuring complete isolation.
    """
    # Truncate all tables to ensure a clean state
    for table in reversed(db.metadata.sorted_tables):
        db.session.execute(table.delete())
    db.session.commit()

    yield db.session

    # The session is already clean for the next test


@pytest.fixture(scope="function")
def client(app):
    """A test client for the app."""
    with app.test_request_context():
        yield app.test_client()
