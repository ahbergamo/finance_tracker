from datetime import date
from app.models.account import Account
from app.models.account_balance_history import AccountBalanceHistory
from app import db
from tests.routes.utils import login


def test_net_worth_requires_login(client):
    """Net worth report requires authentication."""
    response = client.get("/reports/net-worth")
    assert response.status_code == 302
    assert "/login" in response.location


def test_net_worth_report_loads(client, app):
    """Test that net worth report page loads successfully."""
    login(client, "user1", "test123")

    response = client.get("/reports/net-worth")
    assert response.status_code == 200
    assert b"Net Worth" in response.data


def test_net_worth_shows_all_account_types(client, app):
    """Test that net worth report shows different account types."""
    login(client, "user1", "test123")

    response = client.get("/reports/net-worth")
    assert response.status_code == 200

    # Check for account type sections
    assert b"Checking" in response.data
    assert b"Savings" in response.data
    assert b"Credit Card" in response.data
    assert b"Retirement" in response.data
    assert b"Brokerage" in response.data


def test_net_worth_shows_account_names(client, app):
    """Test that net worth report shows individual accounts."""
    login(client, "user1", "test123")

    response = client.get("/reports/net-worth")
    assert response.status_code == 200

    # Check for specific account names
    assert b"Chase Checking" in response.data
    assert b"Chase Savings" in response.data
    assert b"Fidelity 401k" in response.data
    assert b"Vanguard Brokerage" in response.data


def test_net_worth_shows_totals(client, app):
    """Test that net worth report shows asset/liability totals."""
    login(client, "user1", "test123")

    response = client.get("/reports/net-worth")
    assert response.status_code == 200

    # Check for total labels
    assert b"Total Assets" in response.data
    assert b"Total Liabilities" in response.data


def test_net_worth_uses_balance_history_for_retirement(client, app):
    """Test that retirement accounts use balance history for current balance."""
    login(client, "user1", "test123")

    with app.app_context():
        account = Account.query.filter_by(name="Fidelity 401k").first()

        # Add balance history entry
        entry = AccountBalanceHistory(
            account_id=account.id,
            balance=75000.00,
            as_of_date=date(2025, 1, 15)
        )
        db.session.add(entry)
        db.session.commit()

    response = client.get("/reports/net-worth")
    assert response.status_code == 200
    # Should show the balance history value, not initial balance
    assert b"75,000.00" in response.data


def test_net_worth_chart_data(client, app):
    """Test that net worth report includes chart data."""
    login(client, "user1", "test123")

    response = client.get("/reports/net-worth")
    assert response.status_code == 200

    # Check for chart canvas and script
    assert b"netWorthChart" in response.data
    assert b"chart.js" in response.data.lower() or b"Chart" in response.data


def test_net_worth_only_shows_own_family_accounts(client, app):
    """Test that net worth only includes accounts from user's family."""
    login(client, "user1", "test123")

    response = client.get("/reports/net-worth")
    assert response.status_code == 200

    # Should not show family2's accounts
    assert b"US Bank Checking" not in response.data
    assert b"US Bank Savings" not in response.data
