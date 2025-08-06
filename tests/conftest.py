import pytest
from app import create_app, db as _db
from config import TestingConfig

@pytest.fixture(scope='session')
def app():
    """Create and configure a new app instance for each test session."""
    app = create_app(config_class=TestingConfig)
    
    # Establish an application context before running the tests
    with app.app_context():
        yield app

@pytest.fixture(scope='session')
def db(app):
    """Session-wide test database."""
    _db.app = app
    _db.create_all()

    yield _db

    _db.drop_all()

@pytest.fixture(scope='function')
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


@pytest.fixture(scope='function')
def client(app):
    """A test client for the app."""
    return app.test_client()