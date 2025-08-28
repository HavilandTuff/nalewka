import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration class."""

    # Fail loudly if the SECRET_KEY is not set in production.
    SECRET_KEY = os.environ.get("SECRET_KEY") or "a-secret-key-for-development"
    if os.environ.get("FLASK_ENV") == "production" and not SECRET_KEY:
        raise ValueError(
            "No SECRET_KEY set for Flask application in production environment"
        )

    # Handle both development and production database URLs
    database_url = os.environ.get("DATABASE_URL")
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = database_url or "sqlite:///" + os.path.join(
        basedir, "app.db"
    )

    # Additional production settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }


class TestingConfig(Config):
    """Configuration for testing."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False  # Disable CSRF for simpler form testing
    SECRET_KEY = "test-secret-key"
