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
    valid_types = {'checking', 'savings', 'credit_card', 'retirement', 'brokerage', 'real_estate', 'vehicle', 'other_asset', 'loan'}
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


def test_pension_account(app):
    """
    Test creating a pension account with monthly benefit and start date.
    """
    from datetime import date
    family = Family.query.first()
    account = Account(
        name="Test Pension",
        family_id=family.id,
        account_type='retirement',
        retirement_type='pension',
        pension_monthly_benefit=580.17,
        pension_start_date=date(2044, 5, 1)
    )
    db.session.add(account)
    db.session.commit()

    saved = Account.query.filter_by(name="Test Pension").first()
    assert saved is not None
    assert saved.account_type == 'retirement'
    assert saved.retirement_type == 'pension'
    assert float(saved.pension_monthly_benefit) == 580.17
    assert saved.pension_start_date == date(2044, 5, 1)


def test_pension_is_pension_method(app):
    """
    Test the is_pension() helper method.
    """
    from datetime import date
    family = Family.query.first()

    # Pension account
    pension = Account(
        name="Boeing Pension",
        family_id=family.id,
        account_type='retirement',
        retirement_type='pension',
        pension_monthly_benefit=500.00,
        pension_start_date=date(2044, 5, 1)
    )
    db.session.add(pension)

    # Regular retirement account
    retirement = Account(
        name="401k Account",
        family_id=family.id,
        account_type='retirement',
        retirement_type='traditional_401k',
        initial_balance=50000.00
    )
    db.session.add(retirement)
    db.session.commit()

    assert pension.is_pension() is True
    assert retirement.is_pension() is False


def test_pension_present_value_calculation(app):
    """
    Test the pension present value calculation.
    """
    from datetime import date
    family = Family.query.first()

    account = Account(
        name="Test Pension PV",
        family_id=family.id,
        account_type='retirement',
        retirement_type='pension',
        pension_monthly_benefit=1000.00,  # $1000/month
        pension_start_date=date(2044, 5, 1)
    )
    db.session.add(account)
    db.session.commit()

    pv = account.get_pension_present_value()

    # PV should be a positive number
    assert pv > 0
    # With $1000/month for 20 years at 4%, PV should be roughly $163k-170k
    # (discounted back ~19 years from 2044 to 2025)
    # The exact value depends on the calculation date
    assert pv < 200000  # Sanity check - shouldn't be more than simple sum


def test_pension_present_value_no_benefit(app):
    """
    Test that pension PV returns 0 when no benefit is set.
    """
    from decimal import Decimal
    family = Family.query.first()

    account = Account(
        name="Empty Pension",
        family_id=family.id,
        account_type='retirement',
        retirement_type='pension'
    )
    db.session.add(account)
    db.session.commit()

    pv = account.get_pension_present_value()
    assert pv == Decimal('0')


def test_pension_present_value_no_start_date(app):
    """
    Test that pension PV returns 0 when no start date is set.
    """
    from decimal import Decimal
    family = Family.query.first()

    account = Account(
        name="Pension No Date",
        family_id=family.id,
        account_type='retirement',
        retirement_type='pension',
        pension_monthly_benefit=500.00
    )
    db.session.add(account)
    db.session.commit()

    pv = account.get_pension_present_value()
    assert pv == Decimal('0')
