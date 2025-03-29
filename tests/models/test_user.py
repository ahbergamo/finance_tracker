import pytest
from app.models.user import User, load_user


def get_seeded_user():
    """
    Retrieve a seeded user.
    Assumes that a user with username 'user1' exists.
    """
    user = User.query.filter_by(username="user1").first()
    if not user:
        pytest.skip("Seeded user 'user1' not found.")
    return user


def test_set_and_check_password(app):
    """
    Verify that the check_password method works as expected.
    The seed script sets the password for 'user1' to 'test123'.
    """
    user = get_seeded_user()
    assert user.check_password("test123") is True, "Password should match."
    assert user.check_password("wrongpassword") is False, "Incorrect password should not match."


def test_user_relationships(app):
    """
    Verify that the seeded user has the expected relationship attributes.
    Even if there are no transactions or budgets, the attributes should exist.
    """
    user = get_seeded_user()
    # Check that the user has transactions and budgets attributes
    assert hasattr(user, "transactions"), "User should have a transactions relationship."
    assert hasattr(user, "budgets"), "User should have a budgets relationship."
    # If no transactions or budgets are seeded, they should be empty lists.
    assert user.transactions is not None, "Transactions should not be None."
    assert user.budgets is not None, "Budgets should not be None."


def test_load_user(app):
    """
    Verify that the login_manager's user_loader function correctly loads the seeded user.
    """
    user = get_seeded_user()
    loaded_user = load_user(user.id)
    assert loaded_user is not None, "load_user should return a valid user."
    assert loaded_user.id == user.id, "The loaded user ID should match the seeded user."
