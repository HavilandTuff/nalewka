import os

from pydantic import EmailStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or a .env file.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Core application settings
    SECRET_KEY: str = Field(
        ...,
        min_length=16,
        description="Secret key for session management and security.",
    )

    # Database configuration - use environment-specific defaults
    SQLALCHEMY_DATABASE_URI: str = Field(
        default_factory=lambda: _get_database_uri(),
        pattern=r"^sqlite://.*\.db$|^postgresql\+psycopg2://.*$|^sqlite:///:memory:$",
        description="Database connection URI. Supports SQLite and PostgreSQL.",
    )

    # Mail server settings (made optional for deployment)
    MAIL_SERVER: str = Field(
        "smtp.googlemail.com", min_length=1, description="SMTP server address."
    )
    MAIL_PORT: int = Field(587, ge=1, le=65535, description="SMTP server port.")
    MAIL_USE_TLS: bool = Field(
        True, description="Enable TLS for mail server connection."
    )
    MAIL_USERNAME: str = Field(
        "", min_length=0, description="Username for mail server authentication."
    )
    MAIL_PASSWORD: str = Field(
        "", min_length=0, description="Password for mail server authentication."
    )
    ADMIN_EMAIL: EmailStr = Field(
        "admin@example.com",
        description="Administrator's email address for notifications.",
    )

    # reCAPTCHA settings (made optional for deployment)
    RECAPTCHA_PUBLIC_KEY: str = Field(
        "", min_length=0, description="Google reCAPTCHA public key."
    )
    RECAPTCHA_PRIVATE_KEY: str = Field(
        "", min_length=0, description="Google reCAPTCHA private key."
    )

    # Google OAuth settings (made optional for deployment)
    GOOGLE_CLIENT_ID: str = Field(
        "", min_length=0, description="Google OAuth client ID."
    )
    GOOGLE_CLIENT_SECRET: str = Field(
        "", min_length=0, description="Google OAuth client secret."
    )
    GOOGLE_DISCOVERY_URL: str = Field(
        "https://accounts.google.com/.well-known/openid-configuration",
        min_length=1,
        description="Google OpenID Connect discovery URL.",
    )

    # Upload settings
    UPLOAD_FOLDER: str = Field(
        "app/static/uploads", min_length=1, description="Directory for file uploads."
    )
    MAX_CONTENT_LENGTH: int = Field(
        16 * 1024 * 1024,
        ge=0,
        description=(
            "Maximum allowed content length for uploads in bytes (default 16MB)."
        ),
    )

    # Testing settings
    WTF_CSRF_ENABLED: bool = Field(
        True,
        description="Enable CSRF protection for forms.",
    )


def _get_database_uri() -> str:
    """
    Get the appropriate database URI based on the environment.
    On Render, it modifies the DATABASE_URL to be compatible with SQLAlchemy.
    """
    # Check if we're running tests
    if os.environ.get("TESTING") == "1":
        return "sqlite:///:memory:"

    # Check if we're in production (Render)
    if os.environ.get("RENDER") == "true":
        database_url = os.environ.get("DATABASE_URL")
        if database_url and database_url.startswith("postgres://"):
            # SQLAlchemy 2.0 requires 'postgresql+psycopg2://'
            database_url = database_url.replace(
                "postgres://", "postgresql+psycopg2://", 1
            )
        return database_url or "sqlite:///site.db"

    # Default to local SQLite database in instance folder
    return "sqlite:///site.db"


# Instantiate settings to be imported by the application
settings = Settings()  # type: ignore
