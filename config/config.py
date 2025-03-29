import os
import sys


class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "default_secret_key")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    VERSION = "1.1.0"


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///finance_tracker_dev.db"


class ProductionConfig(BaseConfig):
    DEBUG = False

    # Get DB credentials from environment variables
    DB_USER = os.environ.get("DB_USER", "finance_user")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "password")
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = os.environ.get("DB_PORT", "3306")  # Keep as string for compatibility
    DB_NAME = os.environ.get("DB_NAME", "finance_tracker")

    # Ensure all required values exist before formatting URI
    if all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    else:
        print("⚠️ Missing DB environment variables, exiting.")
        # SQLALCHEMY_DATABASE_URI = "sqlite:///finance_tracker_fallback.db"
        sys.exit(1)  # Exit with a failure status code

    # Insert SQLAlchemy engine options to help manage stale connections
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 550  # DB set to 600s timeout, recycle at 550s
    }


class PortableConfig(BaseConfig):
    DEBUG = True  # True for easier debugging
    DB_USER = os.environ.get("DB_USER", "finance_user")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "password")
    DB_HOST = os.environ.get("DB_HOST", "mysql_db")
    DB_PORT = os.environ.get("DB_PORT", "3306")
    DB_NAME = os.environ.get("DB_NAME", "finance_tracker")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 550
    }


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
