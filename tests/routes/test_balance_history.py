from datetime import date
from app.models.account import Account
from app.models.account_balance_history import AccountBalanceHistory
from app import db
from tests.routes.utils import login


def test_balance_history_requires_login(client):
    """Balance history page requires authentication."""
    response = client.get("/accounts/1/balances")
    assert response.status_code == 302
    assert "/login" in response.location


def test_balance_history_index_retirement_account(client, app):
    """Test viewing balance history for a retirement account."""
    login(client, "user1", "test123")

    with app.app_context():
        account = Account.query.filter_by(name="Fidelity 401k").first()
        assert account is not None

        response = client.get(f"/accounts/{account.id}/balances")
        assert response.status_code == 200
        assert b"Fidelity 401k" in response.data
        assert b"Retirement" in response.data


def test_balance_history_index_brokerage_account(client, app):
    """Test viewing balance history for a brokerage account."""
    login(client, "user1", "test123")

    with app.app_context():
        account = Account.query.filter_by(name="Vanguard Brokerage").first()
        assert account is not None

        response = client.get(f"/accounts/{account.id}/balances")
        assert response.status_code == 200
        assert b"Vanguard Brokerage" in response.data
        assert b"Brokerage" in response.data


def test_balance_history_redirects_for_checking_account(client, app):
    """Balance history should redirect for non-retirement/brokerage accounts."""
    login(client, "user1", "test123")

    with app.app_context():
        account = Account.query.filter_by(name="Chase Checking").first()
        assert account is not None

        response = client.get(f"/accounts/{account.id}/balances")
        assert response.status_code == 302


def test_add_balance_entry(client, app):
    """Test adding a balance entry."""
    login(client, "user1", "test123")

    with app.app_context():
        account = Account.query.filter_by(name="Fidelity 401k").first()

        response = client.post(
            f"/accounts/{account.id}/balances/add",
            data={
                "as_of_date": "2025-01-15",
                "balance": "55000.00",
                "notes": "January update"
            },
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b"Balance added successfully" in response.data or b"55,000.00" in response.data

        # Verify entry was created
        entry = AccountBalanceHistory.query.filter_by(account_id=account.id).first()
        assert entry is not None
        assert entry.balance == 55000.00
        assert entry.as_of_date == date(2025, 1, 15)
        assert entry.notes == "January update"


def test_add_balance_updates_existing_date(client, app):
    """Test that adding a balance for existing date updates instead of creating duplicate."""
    login(client, "user1", "test123")

    with app.app_context():
        account = Account.query.filter_by(name="Fidelity 401k").first()

        # Add first entry
        client.post(
            f"/accounts/{account.id}/balances/add",
            data={"as_of_date": "2025-02-01", "balance": "60000.00"},
            follow_redirects=True
        )

        # Add second entry for same date
        response = client.post(
            f"/accounts/{account.id}/balances/add",
            data={"as_of_date": "2025-02-01", "balance": "62000.00"},
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b"Balance updated" in response.data

        # Should only have one entry for that date
        entries = AccountBalanceHistory.query.filter_by(
            account_id=account.id,
            as_of_date=date(2025, 2, 1)
        ).all()
        assert len(entries) == 1
        assert entries[0].balance == 62000.00


def test_delete_balance_entry(client, app):
    """Test deleting a balance entry."""
    login(client, "user1", "test123")

    with app.app_context():
        account = Account.query.filter_by(name="Vanguard Brokerage").first()

        # Add an entry first
        entry = AccountBalanceHistory(
            account_id=account.id,
            balance=30000.00,
            as_of_date=date(2025, 3, 1)
        )
        db.session.add(entry)
        db.session.commit()
        entry_id = entry.id

        response = client.post(
            f"/accounts/{account.id}/balances/{entry_id}/delete",
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b"Balance entry deleted" in response.data

        # Verify entry was deleted
        deleted = AccountBalanceHistory.query.get(entry_id)
        assert deleted is None


def test_balance_history_shows_current_balance(client, app):
    """Test that balance history page shows the most recent balance."""
    login(client, "user1", "test123")

    with app.app_context():
        account = Account.query.filter_by(name="Fidelity 401k").first()

        # Add some balance history
        entries = [
            AccountBalanceHistory(account_id=account.id, balance=51000.00, as_of_date=date(2025, 1, 1)),
            AccountBalanceHistory(account_id=account.id, balance=53000.00, as_of_date=date(2025, 2, 1)),
            AccountBalanceHistory(account_id=account.id, balance=55000.00, as_of_date=date(2025, 3, 1)),
        ]
        db.session.bulk_save_objects(entries)
        db.session.commit()

        response = client.get(f"/accounts/{account.id}/balances")
        assert response.status_code == 200
        # Most recent balance should be displayed prominently
        assert b"55,000.00" in response.data


def test_balance_history_other_family_forbidden(client, app):
    """Test that users cannot access balance history for other families."""
    login(client, "user1", "test123")

    with app.app_context():
        # Get an account from family2 (frank's family)
        account = Account.query.filter_by(name="US Bank Checking").first()
        assert account is not None

        response = client.get(f"/accounts/{account.id}/balances")
        assert response.status_code == 404
