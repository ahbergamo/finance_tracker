from app.services.auth import register_user, authenticate_user
from app.models.user import User
from app import db


def test_register_user(app):
    """
    Test registering a new user and handling duplicate registrations.
    """
    with app.app_context():
        # Ensure a clean slate for users.
        db.session.query(User).delete()
        db.session.commit()

        # Register a new user.
        user = register_user("testuser", "test@example.com", "testpass")
        assert user is not None, "User should be registered successfully."
        assert user.username == "testuser"
        assert user.email == "test@example.com"

        # Attempt to register the same username again; expect None.
        duplicate = register_user("testuser", "test@example.com", "testpass")
        assert duplicate is None, "Duplicate registration should return None."


def test_authenticate_user(app):
    """
    Test that authenticate_user returns the correct user when given valid credentials,
    and returns None for invalid credentials.
    """
    with app.app_context():
        # Clean up and register a new user for authentication.
        db.session.query(User).delete()
        db.session.commit()
        user = register_user("authuser", "auth@example.com", "secret")
        assert user is not None

        # Test successful authentication.
        auth_user = authenticate_user("authuser", "secret")
        assert auth_user is not None, "Valid credentials should return a user."
        assert auth_user.username == "authuser"

        # Test authentication with an invalid password.
        wrong_pass = authenticate_user("authuser", "wrongpassword")
        assert wrong_pass is None, "Invalid password should return None."

        # Test authentication for a non-existent user.
        non_existent = authenticate_user("nonexistent", "any")
        assert non_existent is None, "Non-existent user should return None."
