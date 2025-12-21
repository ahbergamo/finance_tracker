from app.models.account import Account
from app.models.family import Family
from app.models.user import User
from app import db


def test_seeded_accounts(app):
    """
    Verify that accounts have been seeded into the database.
    """
    accounts = Account.query.all()
    assert len(accounts) > 0, "No accounts were seeded."


def test_account_repr(app):
    """
    Check that the __repr__ method of a known seeded account returns the expected string.
    """
    account = Account.query.filter_by(name="Chase Prime Credit").first()
    assert account is not None, "Chase Prime Credit not found in seeded data."

    expected_repr = f"<Account {account.name} (Family ID: {account.family_id})>"
    assert repr(account) == expected_repr


def test_foreign_key_relationship(app):
    """
    Ensure every Account is linked to a valid Family.
    """
    accounts = Account.query.all()
    for account in accounts:
        family = db.session.get(Family, account.family_id)
        assert family is not None, f"Account {account.name} is not linked to a valid Family."


def test_family_has_users(app):
    """
    Confirm that each seeded Family has at least one associated User.
    """
    families = Family.query.all()
    for family in families:
        users = User.query.filter_by(family_id=family.id).all()
        assert len(users) > 0, f"Family {family.name} has no associated users."


def test_account_type_field(app):
    """
    Verify that accounts have proper account_type values.
    """
    accounts = Account.query.all()
    valid_types = {'checking', 'savings', 'credit_card', 'retirement', 'brokerage'}
    for account in accounts:
        assert account.account_type in valid_types, f"Account {account.name} has invalid account_type: {account.account_type}"


def test_initial_balance_default(app):
    """
    Verify that initial_balance defaults to 0.
    """
    account = Account.query.first()
    assert account.initial_balance == 0, "initial_balance should default to 0"


def test_retirement_account_with_retirement_type(app):
    """
    Test creating a retirement account with retirement_type set.
    """
    family = Family.query.first()
    account = Account(
        name="Test 401k",
        family_id=family.id,
        account_type='retirement',
        retirement_type='traditional_401k',
        initial_balance=50000.00
    )
    db.session.add(account)
    db.session.commit()

    saved = Account.query.filter_by(name="Test 401k").first()
    assert saved is not None
    assert saved.account_type == 'retirement'
    assert saved.retirement_type == 'traditional_401k'
    assert saved.initial_balance == 50000.00
    # CSV fields should be nullable for retirement accounts
    assert saved.category_field is None
    assert saved.date_field is None


def test_brokerage_account(app):
    """
    Test creating a brokerage account.
    """
    family = Family.query.first()
    account = Account(
        name="Test Brokerage",
        family_id=family.id,
        account_type='brokerage',
        initial_balance=100000.00
    )
    db.session.add(account)
    db.session.commit()

    saved = Account.query.filter_by(name="Test Brokerage").first()
    assert saved is not None
    assert saved.account_type == 'brokerage'
    assert saved.retirement_type is None  # Not a retirement account
    assert saved.initial_balance == 100000.00
