from datetime import date
from app.models.account import Account
from app.models.account_balance_history import AccountBalanceHistory
from app.models.family import Family
from app import db


def test_create_balance_history(app):
    """
    Test creating an account balance history entry.
    """
    family = Family.query.first()

    # Create a retirement account
    account = Account(
        name="Test Retirement for History",
        family_id=family.id,
        account_type='retirement',
        retirement_type='roth_ira',
        initial_balance=10000.00
    )
    db.session.add(account)
    db.session.commit()

    # Create a balance history entry
    history = AccountBalanceHistory(
        account_id=account.id,
        balance=12500.50,
        as_of_date=date(2025, 1, 15),
        notes="Monthly update"
    )
    db.session.add(history)
    db.session.commit()

    saved = AccountBalanceHistory.query.filter_by(account_id=account.id).first()
    assert saved is not None
    assert saved.balance == 12500.50
    assert saved.as_of_date == date(2025, 1, 15)
    assert saved.notes == "Monthly update"
    assert saved.created_at is not None


def test_balance_history_relationship(app):
    """
    Test the relationship between Account and AccountBalanceHistory.
    """
    family = Family.query.first()

    account = Account(
        name="Test Account with History",
        family_id=family.id,
        account_type='brokerage',
        initial_balance=50000.00
    )
    db.session.add(account)
    db.session.commit()

    # Add multiple balance history entries
    entries = [
        AccountBalanceHistory(account_id=account.id, balance=50000.00, as_of_date=date(2025, 1, 1)),
        AccountBalanceHistory(account_id=account.id, balance=52000.00, as_of_date=date(2025, 2, 1)),
        AccountBalanceHistory(account_id=account.id, balance=51500.00, as_of_date=date(2025, 3, 1)),
    ]
    db.session.bulk_save_objects(entries)
    db.session.commit()

    # Verify relationship
    history = AccountBalanceHistory.query.filter_by(account_id=account.id).order_by(AccountBalanceHistory.as_of_date).all()
    assert len(history) == 3
    assert history[0].balance == 50000.00
    assert history[1].balance == 52000.00
    assert history[2].balance == 51500.00


def test_balance_history_repr(app):
    """
    Test the __repr__ method of AccountBalanceHistory.
    """
    family = Family.query.first()

    account = Account(
        name="Repr Test Account",
        family_id=family.id,
        account_type='retirement',
        retirement_type='traditional_ira'
    )
    db.session.add(account)
    db.session.commit()

    history = AccountBalanceHistory(
        account_id=account.id,
        balance=25000.00,
        as_of_date=date(2025, 6, 15)
    )
    db.session.add(history)
    db.session.commit()

    expected = f"<AccountBalanceHistory {account.id} $25000.00 @ 2025-06-15>"
    assert repr(history) == expected


def test_balance_history_without_notes(app):
    """
    Test that notes field is optional.
    """
    family = Family.query.first()

    account = Account(
        name="No Notes Account",
        family_id=family.id,
        account_type='brokerage'
    )
    db.session.add(account)
    db.session.commit()

    history = AccountBalanceHistory(
        account_id=account.id,
        balance=75000.00,
        as_of_date=date(2025, 4, 1)
    )
    db.session.add(history)
    db.session.commit()

    saved = AccountBalanceHistory.query.filter_by(account_id=account.id).first()
    assert saved.notes is None
