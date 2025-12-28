import os
import subprocess
from typing import Any, Dict, Optional

from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

from app.error_handlers import register_error_handlers
from config import settings

# Extensions are initialized here but not attached to an app
db: SQLAlchemy = SQLAlchemy()
migrate: Migrate = Migrate()
login: LoginManager = LoginManager()
login.login_view = "main.login"
login.login_message = "Please log in to access this page."
csrf = CSRFProtect()


def get_git_commit_hash() -> Optional[str]:
    """Function to get the short git commit hash."""
    try:
        # Run the git command to get the short hash
        commit_hash = (
            subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL
            )
            .decode("utf-8")
            .strip()
        )
        return commit_hash
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Handle cases where it's not a git repo or git is not installed
        return None


def create_app(config_override: Optional[Dict[str, Any]] = None) -> Flask:
    # Set instance path to ensure database files are in the right location
    instance_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "..", "instance"
    )

    app: Flask = Flask(
        __name__, instance_path=instance_path, instance_relative_config=True
    )

    # Load baseline configuration from settings
    config_dict: Dict[str, Any] = settings.model_dump()
    for key, value in config_dict.items():
        app.config[key] = value

    # Apply configuration overrides if provided
    if config_override:
        for key, value in config_override.items():
            app.config[key] = value

    # Special handling for SQLALCHEMY_ENGINE_OPTIONS
    if hasattr(settings, "SQLALCHEMY_ENGINE_OPTIONS"):
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = settings.SQLALCHEMY_ENGINE_OPTIONS

    app.config["GIT_COMMIT_HASH"] = get_git_commit_hash()
    if app.config["GIT_COMMIT_HASH"] is None:
        app.config["GIT_COMMIT_HASH"] = "unknown"

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    csrf.init_app(app)

    # Initialize logging
    if not app.debug and not app.testing:
        import logging
        from logging.handlers import RotatingFileHandler

        # Ensure log directory exists
        log_dir = os.path.join(app.root_path, "..", os.path.dirname(settings.LOG_FILE))
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_path = os.path.join(app.root_path, "..", settings.LOG_FILE)
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=settings.LOG_MAX_BYTES,
            backupCount=settings.LOG_BACKUP_COUNT,
        )
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
            )
        )
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        if settings.LOG_TO_STDOUT:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info("Nalewka startup")

    # Import and register the blueprints
    from app.api import api_bp
    from app.routes import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)

    # Register error handlers
    register_error_handlers(app)

    @app.context_processor
    def inject_git_hash() -> Dict[str, str]:
        """Injects the git commit hash into all templates."""
        return dict(git_commit_hash=app.config["GIT_COMMIT_HASH"])  # type: ignore

    return app
