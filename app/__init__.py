import os
import subprocess
from typing import Any, Dict, Optional

from flask import Flask, render_template
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

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

    # Load configuration
    if config_override:
        for key, value in config_override.items():
            app.config[key] = value
    else:
        config_dict: Dict[str, Any] = settings.model_dump()
        for key, value in config_dict.items():
            app.config[key] = value

    app.config["GIT_COMMIT_HASH"] = get_git_commit_hash()
    if app.config["GIT_COMMIT_HASH"] is None:
        app.config["GIT_COMMIT_HASH"] = "unknown"

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    csrf.init_app(app)

    # Import and register the blueprints
    from app.api import api_bp
    from app.routes import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)

    # Register error handlers on the app
    @app.errorhandler(404)
    def not_found_error(error: Any) -> Any:
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(error: Any) -> Any:
        db.session.rollback()
        return render_template("500.html"), 500

    @app.context_processor
    def inject_git_hash() -> Dict[str, str]:
        """Injects the git commit hash into all templates."""
        return dict(git_commit_hash=app.config["GIT_COMMIT_HASH"])  # type: ignore

    return app
