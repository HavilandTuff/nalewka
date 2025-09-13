import os

from pydantic import EmailStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or a .env file.

    For Raspberry Pi Zero deployment, consider using SQLite for better performance
    on resource-constrained devices. See DEPLOY_PI_ZERO.md for more details.
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
        description="Database connection URI. Supports SQLite and PostgreSQL.",
    )

    # SQLAlchemy engine options for performance on resource-constrained devices
    SQLALCHEMY_ENGINE_OPTIONS: dict = Field(
        default_factory=lambda: {
            "pool_pre_ping": True,
            "pool_recycle": 300,
            "pool_size": 2,  # Reduced pool size for Pi Zero
            "max_overflow": 0,
        },
        description="SQLAlchemy engine options. Optimized for Raspberry Pi Zero.",
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
    """Get the appropriate database URI based on the environment."""
    # Check if we're running tests
    if os.environ.get("TESTING") == "1":
        return "sqlite:///:memory:"

    # Check for DATABASE_URL environment variable (used in production on Render)
    if database_url := os.environ.get("DATABASE_URL"):
        return database_url

    # Default to local SQLite database in instance folder
    return "sqlite:///site.db"


# Instantiate settings to be imported by the application
settings = Settings()  # type: ignore
