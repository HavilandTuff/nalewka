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

    This fixture begins a nested transaction (SAVEPOINT) before the test runs,
    and rolls it back after the test completes. This ensures that tests are
    fully isolated and changes are not persisted to the database, even if the
    test code calls `db.session.commit()`.
    """
    # The db.session object is a scoped_session managed by Flask-SQLAlchemy.
    # We can start a nested transaction on it.
    db.session.begin_nested()
    yield db.session
    db.session.rollback()


@pytest.fixture(scope="function")
def client(app):
    """A test client for the app."""
    with app.test_request_context():
        yield app.test_client()
