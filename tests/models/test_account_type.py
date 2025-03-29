from app.models.account_type import AccountType
from app.models.family import Family
from app.models.user import User
from app import db


def test_seeded_account_types(app):
    """
    Verify that account types have been seeded into the database.
    """
    account_types = AccountType.query.all()
    assert len(account_types) > 0, "No account types were seeded."


def test_account_type_repr(app):
    """
    Check that the __repr__ method of a known seeded account type returns the expected string.
    """
    # For example, in your seed script the first family seeds an account type "Chase Prime Credit"
    account_type = AccountType.query.filter_by(name="Chase Prime Credit").first()
    assert account_type is not None, "Chase Prime Credit not found in seeded data."

    expected_repr = f"<AccountType {account_type.name} (Family ID: {account_type.family_id})>"
    assert repr(account_type) == expected_repr


def test_foreign_key_relationship(app):
    """
    Ensure every AccountType is linked to a valid Family.
    """
    account_types = AccountType.query.all()
    for account_type in account_types:
        family = db.session.get(Family, account_type.family_id)
        assert family is not None, f"AccountType {account_type.name} is not linked to a valid Family."


def test_family_has_users(app):
    """
    Confirm that each seeded Family has at least one associated User.
    """
    families = Family.query.all()
    for family in families:
        users = User.query.filter_by(family_id=family.id).all()
        assert len(users) > 0, f"Family {family.name} has no associated users."
