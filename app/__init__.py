from flask import Flask, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
import os
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from datetime import timedelta
from flask_session import Session
import redis


# Load environment variables from .env
load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()

# Determine which configuration to use based on the FLASK_CONFIG environment variable
config_object = os.environ.get("FLASK_CONFIG", "config.config.DevelopmentConfig")


def create_app(test_config=None):
    app = Flask(__name__)

    if test_config:
        app.config.update(test_config)
    else:
        app.config.from_object(config_object)

    # Ensure a secret key is set for sessions
    app.secret_key = os.environ.get("SECRET_KEY", "default_secret_key")

    if not app.debug:
        app.config.update(
            SESSION_COOKIE_SECURE=True,     # Only send over HTTPS
            SESSION_COOKIE_HTTPONLY=True,   # Not accessible to JavaScript
            SESSION_COOKIE_SAMESITE="Lax",  # Protect against CSRF
        )

    app.config.setdefault('REMEMBER_COOKIE_DURATION', timedelta(days=30))
    app.config["SESSION_TYPE"] = "redis"
    app.config["SESSION_PERMANENT"] = True

    # You're using Redis for server-side session storage
    # You’re running HTTPS in production
    # You're not exposing HTTP local dev to the internet
    # you are safe to remove this line:
    # app.config["SESSION_USE_SIGNER"] = True

    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
    app.config["SESSION_REDIS"] = redis.from_url(redis_url)
    Session(app)

    # Inject version globally
    @app.context_processor
    def inject_version():
        return dict(version=app.config.get('VERSION', '1.0.0'))

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    migrate.init_app(app, db)
    csrf.init_app(app)

    # Import and register blueprints
    from app.routes.auth import auth_bp
    from app.routes.transactions import transactions_bp
    from app.routes.budgets import budgets_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.categories import categories_bp
    from app.routes.profile import profile_bp
    from app.routes.account_types import account_types_bp
    from app.routes.import_rules import import_rules_bp
    from app.routes.reports import report_bp
    from app.routes.help import help_bp

    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User  # Local import to avoid circular dependency
        return db.session.get(User, int(user_id))

    app.register_blueprint(auth_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(budgets_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(account_types_bp)
    app.register_blueprint(import_rules_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(help_bp)

    # Default route that redirects to the login page
    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard.dashboard"))
        else:
            return redirect(url_for("auth.login"))

    # Register global error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('error/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('error/500.html'), 500

    try:
        from app.cli import seed_db
        app.cli.add_command(seed_db)
    except ImportError:
        # If app.cli doesn't exist in your local environment
        # (like on GitHub), just skip it
        pass

    if not app.debug and not app.testing:
        setup_logging(app)

    app.logger.info(f"Finance Tracker startup using config: {config_object}")

    return app


def setup_logging(app):
    """Configures logging for production."""
    log_dir = "logs"
    log_file = os.path.join(log_dir, "finance_tracker.log")

    log_level = logging.INFO if "ProductionConfig" in config_object else logging.DEBUG

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    file_handler = RotatingFileHandler(log_file, maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
    ))
    file_handler.setLevel(log_level)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(log_level)
