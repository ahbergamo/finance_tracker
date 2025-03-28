import pytest
from app import create_app, db
from tests.seed_test_data import seed_db_for_tests


@pytest.fixture
def app():
    # Seemed to be the only way to get this to work without
    # the test using the dev sqlite file.
    test_config = {
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
    }
    app = create_app(test_config)

    with app.app_context():
        db.create_all()
        seed_db_for_tests()  # Seed the database
        yield app  # testing happens here
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
