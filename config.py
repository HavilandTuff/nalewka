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
    SQLALCHEMY_DATABASE_URI: str = Field(
        "sqlite:///site.db",
        pattern=r"^sqlite:///.*\.db$|^postgresql\+psycopg2://.*$",
        description="Database connection URI. Supports SQLite and PostgreSQL.",
    )

    # Mail server settings
    MAIL_SERVER: str = Field(
        "smtp.googlemail.com", min_length=1, description="SMTP server address."
    )
    MAIL_PORT: int = Field(587, ge=1, le=65535, description="SMTP server port.")
    MAIL_USE_TLS: bool = Field(
        True, description="Enable TLS for mail server connection."
    )
    MAIL_USERNAME: str = Field(
        ..., min_length=1, description="Username for mail server authentication."
    )
    MAIL_PASSWORD: str = Field(
        ..., min_length=1, description="Password for mail server authentication."
    )
    ADMIN_EMAIL: EmailStr = Field(
        ..., description="Administrator's email address for notifications."
    )

    # reCAPTCHA settings
    RECAPTCHA_PUBLIC_KEY: str = Field(
        ..., min_length=1, description="Google reCAPTCHA public key."
    )
    RECAPTCHA_PRIVATE_KEY: str = Field(
        ..., min_length=1, description="Google reCAPTCHA private key."
    )

    # Google OAuth settings
    GOOGLE_CLIENT_ID: str = Field(
        ..., min_length=1, description="Google OAuth client ID."
    )
    GOOGLE_CLIENT_SECRET: str = Field(
        ..., min_length=1, description="Google OAuth client secret."
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


# Instantiate settings to be imported by the application
settings = Settings()  # type: ignore
