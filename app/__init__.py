import subprocess

from flask import Flask, render_template
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

# Extensions are initialized here but not attached to an app
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = "login"
login.login_message = "Please log in to access this page."


def get_git_commit_hash():
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


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.config["GIT_COMMIT_HASH"] = get_git_commit_hash()
    if app.config["GIT_COMMIT_HASH"] is None:
        app.config["GIT_COMMIT_HASH"] = "unknown"

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    # Import and register the blueprint
    from app.routes import main_bp

    app.register_blueprint(main_bp)

    # Register error handlers on the app
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("500.html"), 500

    @app.context_processor
    def inject_git_hash():
        """Injects the git commit hash into all templates."""
        return dict(git_commit_hash=app.config.get("GIT_COMMIT_HASH"))

    return app
