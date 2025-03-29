from app import db
from app.models.user import User
from flask import current_app


def register_user(username, email, password):
    """
    Registers a new user in the system.

    Args:
        username (str): The username of the new user.
        email (str): The email address of the new user.
        password (str): The password for the new user.

    Returns:
        User: The newly created user object if registration is successful.
        None: If a user with the same username already exists.
    """
    current_app.logger.debug("Attempting to register user: %s", username)
    if User.query.filter_by(username=username).first():
        current_app.logger.warning("Registration failed: Username '%s' already exists", username)
        return None
    try:
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        current_app.logger.info("User '%s' registered successfully", username)
        return user
    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Error registering user '%s': %s", username, e)
        return None


def authenticate_user(username, password):
    """
    Authenticates a user by verifying their username and password.

    Args:
        username (str): The username of the user.
        password (str): The password of the user.

    Returns:
        User: The authenticated user object if credentials are valid.
        None: If authentication fails.
    """
    current_app.logger.debug("Attempting to authenticate user: %s", username)
    try:
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            current_app.logger.info("User '%s' authenticated successfully", username)
            return user
        else:
            current_app.logger.warning("Authentication failed for user: %s", username)
            return None
    except Exception as e:
        current_app.logger.error("Error authenticating user '%s': %s", username, e)
        return None
