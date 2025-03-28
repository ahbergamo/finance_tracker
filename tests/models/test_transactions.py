import datetime
import pytest
from app import db
from app.models.transaction import Transaction
from app.models.user import User
from app.models.category import Category
from app.models.account_type import AccountType


def get_seeded_user():
    """
    Retrieve a seeded user.
    Assumes that a user with username 'user1' exists.
    """
    user = User.query.filter_by(username="user1").first()
    if not user:
        pytest.skip("Seeded user 'user1' not found.")
    return user


def get_seeded_category():
    """
    Retrieve a seeded category.
    Assumes that a category named 'Credit Card Payment' exists.
    """
    category = Category.query.filter_by(name="Credit Card Payment").first()
    if not category:
        pytest.skip("Seeded category 'Credit Card Payment' not found.")
    return category


def get_seeded_account_type():
    """
    Retrieve a seeded account type.
    Assumes that an account type with name 'Chase Prime Credit' exists.
    """
    account_type = AccountType.query.filter_by(name="Chase Prime Credit").first()
    if not account_type:
        pytest.skip("Seeded account type 'Chase Prime Credit' not found.")
    return account_type


def test_transaction_creation(app):
    """
    Verify that a Transaction can be created using seeded data.
    Checks the field values, default timestamp, and foreign key assignments.
    """
    user = get_seeded_user()
    category = get_seeded_category()
    account_type = get_seeded_account_type()

    # Create a new transaction.
    transaction = Transaction(
        amount=123.45,
        description="Test Transaction",
        user_id=user.id,
        category_id=category.id,
        account_id=account_type.id,
        is_transfer=False
    )
    db.session.add(transaction)
    db.session.commit()

    # Fetch the transaction from the database.
    fetched_transaction = db.session.get(Transaction, transaction.id)
    assert fetched_transaction is not None
    assert fetched_transaction.amount == 123.45
    assert fetched_transaction.description == "Test Transaction"
    assert fetched_transaction.user_id == user.id
    assert fetched_transaction.category_id == category.id
    assert fetched_transaction.account_id == account_type.id
    assert fetched_transaction.is_transfer is False

    # Verify that the timestamp is set to a datetime object and is recent.
    assert isinstance(fetched_transaction.timestamp, datetime.datetime)
    now = datetime.datetime.utcnow()  # use naive UTC datetime
    # Ensure the timestamp is within the last 60 seconds.
    assert (now - fetched_transaction.timestamp).total_seconds() < 60


def test_transaction_relationships(app):
    """
    Verify that the Transaction relationships to Category and AccountType work as expected.
    """
    user = get_seeded_user()
    category = get_seeded_category()
    account_type = get_seeded_account_type()

    transaction = Transaction(
        amount=50.0,
        description="Relationship Test",
        user_id=user.id,
        category_id=category.id,
        account_id=account_type.id,
        is_transfer=True
    )
    db.session.add(transaction)
    db.session.commit()

    # Test that the relationship properties are correctly populated.
    assert transaction.category.id == category.id
    assert transaction.account.id == account_type.id

    # Verify the reverse relationship (backrefs).
    assert transaction in category.transactions
    assert transaction in account_type.transactions
