from datetime import date
from app import db
from app.models.account import Account
from app.models.account_balance_history import AccountBalanceHistory
from app.models.family import Family
from app.models.user import User
from app.services.reports.retirement import (
    get_retirement_accounts,
    get_retirement_account_balances,
)


def test_get_retirement_accounts(app):
    """Test that get_retirement_accounts returns only retirement accounts."""
    family = Family.query.first()

    # Create a retirement account
    retirement = Account(
        name="Test 401k",
        family_id=family.id,
        account_type='retirement',
        retirement_type='traditional_401k',
        initial_balance=50000.00
    )
    db.session.add(retirement)

    # Create a non-retirement account
    checking = Account(
        name="Test Checking",
        family_id=family.id,
        account_type='checking',
        initial_balance=1000.00
    )
    db.session.add(checking)
    db.session.commit()

    accounts = get_retirement_accounts(family.id)
    account_names = [a.name for a in accounts]

    assert "Test 401k" in account_names
    assert "Test Checking" not in account_names


def test_get_retirement_account_balances_with_balance_history(app):
    """Test that retirement account balances are retrieved from balance history."""
    family = Family.query.first()
    user = User.query.filter_by(family_id=family.id).first()

    # Create a retirement account
    account = Account(
        name="Test IRA Balance History",
        family_id=family.id,
        account_type='retirement',
        retirement_type='traditional_ira',
        initial_balance=10000.00
    )
    db.session.add(account)
    db.session.commit()

    # Add balance history entries
    entry1 = AccountBalanceHistory(
        account_id=account.id,
        as_of_date=date(2024, 1, 1),
        balance=12000.00
    )
    entry2 = AccountBalanceHistory(
        account_id=account.id,
        as_of_date=date(2024, 6, 1),
        balance=15000.00
    )
    db.session.add_all([entry1, entry2])
    db.session.commit()

    # Mock current_user
    class MockUser:
        def __init__(self, user):
            self.id = user.id
            self.family_id = user.family_id

    mock_user = MockUser(user)

    # Get balances as of a date after the latest entry
    balances, details = get_retirement_account_balances(mock_user, date(2024, 12, 31))

    # Find the test account in details
    test_account = next((d for d in details if d['name'] == "Test IRA Balance History"), None)
    assert test_account is not None
    assert test_account['balance'] == 15000.00


def test_get_retirement_account_balances_pension(app):
    """Test that pension accounts use present value calculation."""
    family = Family.query.first()
    user = User.query.filter_by(family_id=family.id).first()

    # Create a pension account
    account = Account(
        name="Test Pension Account",
        family_id=family.id,
        account_type='retirement',
        retirement_type='pension',
        pension_monthly_benefit=1000.00,
        pension_start_date=date(2044, 5, 1)
    )
    db.session.add(account)
    db.session.commit()

    class MockUser:
        def __init__(self, user):
            self.id = user.id
            self.family_id = user.family_id

    mock_user = MockUser(user)

    balances, details = get_retirement_account_balances(mock_user, date(2024, 12, 31))

    # Find the pension account in details
    pension_account = next((d for d in details if d['name'] == "Test Pension Account"), None)
    assert pension_account is not None
    assert pension_account['is_pension'] is True
    assert pension_account['pension_monthly_benefit'] == 1000.00
    assert pension_account['balance'] > 0  # Should have calculated PV


def test_get_retirement_account_balances_uses_initial_balance_when_no_history(app):
    """Test that initial_balance is used when no balance history exists."""
    family = Family.query.first()
    user = User.query.filter_by(family_id=family.id).first()

    # Create a retirement account with no balance history
    account = Account(
        name="Test 403b No History",
        family_id=family.id,
        account_type='retirement',
        retirement_type='403b',
        initial_balance=25000.00
    )
    db.session.add(account)
    db.session.commit()

    class MockUser:
        def __init__(self, user):
            self.id = user.id
            self.family_id = user.family_id

    mock_user = MockUser(user)

    balances, details = get_retirement_account_balances(mock_user, date(2024, 12, 31))

    # Find the test account
    test_account = next((d for d in details if d['name'] == "Test 403b No History"), None)
    assert test_account is not None
    assert test_account['balance'] == 25000.00
