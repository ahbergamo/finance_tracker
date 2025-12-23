"""Tests for net worth calculation service."""
from datetime import date
from decimal import Decimal
from app.models.account import Account
from app.models.account_balance_history import AccountBalanceHistory
from app.models.transaction import Transaction
from app.models.category import Category
from app.services.reports.net_worth import (
    get_transaction_based_balance,
    get_balance_history_balance,
    get_account_balance,
    get_net_worth_summary,
)
from app import db


def get_category(app):
    """Get a seeded category for transactions."""
    category = Category.query.first()
    return category.id if category else None


class TestTransactionBasedBalance:
    """Tests for transaction-based account balance calculation."""

    def test_balance_with_no_transactions(self, app):
        """Balance should equal initial_balance when no transactions exist."""
        with app.app_context():
            account = Account.query.filter_by(name="Chase Checking").first()
            # Set a known initial balance
            account.initial_balance = Decimal("1000.00")
            db.session.commit()

            balance = get_transaction_based_balance(account, [1, 2])
            assert balance == 1000.00

    def test_balance_with_transactions(self, app):
        """Balance should be initial_balance + sum of transactions."""
        with app.app_context():
            account = Account.query.filter_by(name="Chase Checking").first()
            account.initial_balance = Decimal("1000.00")
            category_id = get_category(app)
            db.session.commit()

            # Add some transactions
            txn1 = Transaction(
                user_id=1, account_id=account.id, amount=500.00,
                description="Deposit", timestamp=date(2025, 1, 15),
                category_id=category_id
            )
            txn2 = Transaction(
                user_id=1, account_id=account.id, amount=-200.00,
                description="Withdrawal", timestamp=date(2025, 1, 20),
                category_id=category_id
            )
            db.session.add_all([txn1, txn2])
            db.session.commit()

            balance = get_transaction_based_balance(account, [1, 2])
            # 1000 + 500 - 200 = 1300
            assert balance == 1300.00

    def test_balance_with_as_of_date(self, app):
        """Balance should only include transactions up to as_of_date."""
        with app.app_context():
            account = Account.query.filter_by(name="Chase Checking").first()
            account.initial_balance = Decimal("1000.00")
            category_id = get_category(app)
            db.session.commit()

            txn1 = Transaction(
                user_id=1, account_id=account.id, amount=500.00,
                description="Early deposit", timestamp=date(2025, 1, 10),
                category_id=category_id
            )
            txn2 = Transaction(
                user_id=1, account_id=account.id, amount=300.00,
                description="Late deposit", timestamp=date(2025, 1, 25),
                category_id=category_id
            )
            db.session.add_all([txn1, txn2])
            db.session.commit()

            # As of Jan 15, should only include first transaction
            balance = get_transaction_based_balance(account, [1, 2], date(2025, 1, 15))
            # 1000 + 500 = 1500 (not including the 300)
            assert balance == 1500.00


class TestBalanceHistoryBalance:
    """Tests for balance-history account balance calculation."""

    def test_balance_with_no_history_uses_initial(self, app):
        """Should return initial_balance when no history exists."""
        with app.app_context():
            account = Account.query.filter_by(name="Fidelity 401k").first()
            account.initial_balance = Decimal("50000.00")
            db.session.commit()

            # Clear any existing history
            AccountBalanceHistory.query.filter_by(account_id=account.id).delete()
            db.session.commit()

            balance = get_balance_history_balance(account)
            assert balance == 50000.00

    def test_balance_returns_most_recent_entry(self, app):
        """Should return the most recent balance entry."""
        with app.app_context():
            account = Account.query.filter_by(name="Fidelity 401k").first()
            account.initial_balance = Decimal("50000.00")

            # Clear existing and add known history
            AccountBalanceHistory.query.filter_by(account_id=account.id).delete()

            entries = [
                AccountBalanceHistory(account_id=account.id, balance=51000.00, as_of_date=date(2025, 1, 1)),
                AccountBalanceHistory(account_id=account.id, balance=53000.00, as_of_date=date(2025, 2, 1)),
                AccountBalanceHistory(account_id=account.id, balance=55000.00, as_of_date=date(2025, 3, 1)),
            ]
            db.session.add_all(entries)
            db.session.commit()

            balance = get_balance_history_balance(account)
            assert balance == 55000.00

    def test_balance_with_as_of_date(self, app):
        """Should return balance as of specific date."""
        with app.app_context():
            account = Account.query.filter_by(name="Fidelity 401k").first()
            account.initial_balance = Decimal("50000.00")

            AccountBalanceHistory.query.filter_by(account_id=account.id).delete()

            entries = [
                AccountBalanceHistory(account_id=account.id, balance=51000.00, as_of_date=date(2025, 1, 1)),
                AccountBalanceHistory(account_id=account.id, balance=53000.00, as_of_date=date(2025, 2, 1)),
                AccountBalanceHistory(account_id=account.id, balance=55000.00, as_of_date=date(2025, 3, 1)),
            ]
            db.session.add_all(entries)
            db.session.commit()

            # As of Jan 15, should return Jan 1 balance
            balance = get_balance_history_balance(account, date(2025, 1, 15))
            assert balance == 51000.00

            # As of Feb 15, should return Feb 1 balance
            balance = get_balance_history_balance(account, date(2025, 2, 15))
            assert balance == 53000.00

    def test_balance_before_first_entry_uses_initial(self, app):
        """Should return initial_balance if as_of_date is before first entry."""
        with app.app_context():
            account = Account.query.filter_by(name="Fidelity 401k").first()
            account.initial_balance = Decimal("50000.00")

            AccountBalanceHistory.query.filter_by(account_id=account.id).delete()

            entry = AccountBalanceHistory(
                account_id=account.id, balance=55000.00, as_of_date=date(2025, 3, 1)
            )
            db.session.add(entry)
            db.session.commit()

            # As of Jan 1 (before any entries), should return initial
            balance = get_balance_history_balance(account, date(2025, 1, 1))
            assert balance == 50000.00


class TestGetAccountBalance:
    """Tests for the unified get_account_balance function."""

    def test_checking_uses_transaction_based(self, app):
        """Checking accounts should use transaction-based calculation."""
        with app.app_context():
            account = Account.query.filter_by(name="Chase Checking").first()
            account.initial_balance = Decimal("1000.00")
            db.session.commit()

            balance = get_account_balance(account, [1, 2])
            # Should include initial + transactions
            assert isinstance(balance, float)

    def test_retirement_uses_balance_history(self, app):
        """Retirement accounts should use balance history."""
        with app.app_context():
            account = Account.query.filter_by(name="Fidelity 401k").first()
            account.initial_balance = Decimal("50000.00")

            AccountBalanceHistory.query.filter_by(account_id=account.id).delete()
            entry = AccountBalanceHistory(
                account_id=account.id, balance=75000.00, as_of_date=date(2025, 1, 1)
            )
            db.session.add(entry)
            db.session.commit()

            balance = get_account_balance(account, [1, 2])
            assert balance == 75000.00

    def test_brokerage_uses_balance_history(self, app):
        """Brokerage accounts should use balance history."""
        with app.app_context():
            account = Account.query.filter_by(name="Vanguard Brokerage").first()
            account.initial_balance = Decimal("25000.00")

            AccountBalanceHistory.query.filter_by(account_id=account.id).delete()
            entry = AccountBalanceHistory(
                account_id=account.id, balance=30000.00, as_of_date=date(2025, 1, 1)
            )
            db.session.add(entry)
            db.session.commit()

            balance = get_account_balance(account, [1, 2])
            assert balance == 30000.00


class TestNetWorthSummary:
    """Tests for overall net worth calculation."""

    def test_net_worth_sums_all_accounts(self, app):
        """Net worth should correctly sum all account balances."""
        with app.app_context():
            from app.models.user import User
            user = User.query.filter_by(username="user1").first()

            # Set known balances
            checking = Account.query.filter_by(name="Chase Checking").first()
            checking.initial_balance = Decimal("5000.00")

            savings = Account.query.filter_by(name="Chase Savings").first()
            savings.initial_balance = Decimal("10000.00")

            retirement = Account.query.filter_by(name="Fidelity 401k").first()
            retirement.initial_balance = Decimal("50000.00")
            AccountBalanceHistory.query.filter_by(account_id=retirement.id).delete()

            brokerage = Account.query.filter_by(name="Vanguard Brokerage").first()
            brokerage.initial_balance = Decimal("25000.00")
            AccountBalanceHistory.query.filter_by(account_id=brokerage.id).delete()

            db.session.commit()

            result = get_net_worth_summary(user)

            # All positive balances = assets
            # 5000 + 10000 + 50000 + 25000 = 90000
            assert result['total_assets'] == 90000.00
            assert result['total_liabilities'] == 0
            assert result['net_worth'] == 90000.00

    def test_credit_card_negative_is_liability(self, app):
        """Credit card with negative balance should count as liability."""
        with app.app_context():
            from app.models.user import User
            user = User.query.filter_by(username="user1").first()
            category_id = get_category(app)

            # Set up a credit card with debt
            credit = Account.query.filter_by(name="Discover Credit").first()
            if not credit:
                credit = Account(
                    name="Discover Credit",
                    family_id=user.family_id,
                    account_type="credit_card",
                    initial_balance=Decimal("0.00")
                )
                db.session.add(credit)
                db.session.commit()

            # Add transaction representing debt (negative balance)
            txn = Transaction(
                user_id=user.id, account_id=credit.id, amount=-1500.00,
                description="Credit card charges", timestamp=date(2025, 1, 15),
                category_id=category_id
            )
            db.session.add(txn)
            db.session.commit()

            result = get_net_worth_summary(user)

            # Credit card debt should be in liabilities
            assert result['total_liabilities'] >= 1500.00

    def test_accounts_grouped_by_type(self, app):
        """Accounts should be grouped correctly by type in summary."""
        with app.app_context():
            from app.models.user import User
            user = User.query.filter_by(username="user1").first()

            result = get_net_worth_summary(user)

            assert 'checking' in result['summary']
            assert 'savings' in result['summary']
            assert 'credit_card' in result['summary']
            assert 'retirement' in result['summary']
            assert 'brokerage' in result['summary']
            assert 'real_estate' in result['summary']
            assert 'vehicle' in result['summary']
            assert 'other_asset' in result['summary']
            assert 'loan' in result['summary']

            # Check that accounts are in correct groups
            checking_names = [a['name'] for a in result['summary']['checking']['accounts']]
            assert "Chase Checking" in checking_names

            retirement_names = [a['name'] for a in result['summary']['retirement']['accounts']]
            assert "Fidelity 401k" in retirement_names

    def test_real_estate_is_asset(self, app):
        """Real estate should be counted as an asset."""
        with app.app_context():
            from app.models.user import User
            user = User.query.filter_by(username="user1").first()

            # Create a real estate account
            house = Account(
                name="Primary Residence",
                family_id=user.family_id,
                account_type="real_estate",
                initial_balance=Decimal("350000.00")
            )
            db.session.add(house)
            db.session.commit()

            result = get_net_worth_summary(user)

            # Real estate should be in assets
            assert result['summary']['real_estate']['total'] == 350000.00
            assert result['total_assets'] >= 350000.00

    def test_vehicle_is_asset(self, app):
        """Vehicle should be counted as an asset."""
        with app.app_context():
            from app.models.user import User
            user = User.query.filter_by(username="user1").first()

            car = Account(
                name="Honda Accord",
                family_id=user.family_id,
                account_type="vehicle",
                initial_balance=Decimal("25000.00")
            )
            db.session.add(car)
            db.session.commit()

            result = get_net_worth_summary(user)

            assert result['summary']['vehicle']['total'] == 25000.00
            assert result['total_assets'] >= 25000.00

    def test_loan_is_liability(self, app):
        """Loan should always be counted as a liability."""
        with app.app_context():
            from app.models.user import User
            user = User.query.filter_by(username="user1").first()

            mortgage = Account(
                name="Mortgage",
                family_id=user.family_id,
                account_type="loan",
                initial_balance=Decimal("280000.00")
            )
            db.session.add(mortgage)
            db.session.commit()

            result = get_net_worth_summary(user)

            # Loan should be in liabilities (stored as positive, counted as liability)
            assert result['summary']['loan']['total'] == 280000.00
            assert result['total_liabilities'] >= 280000.00

    def test_real_estate_uses_balance_history(self, app):
        """Real estate should use balance history for current value."""
        with app.app_context():
            from app.models.user import User
            user = User.query.filter_by(username="user1").first()

            house = Account(
                name="Beach House",
                family_id=user.family_id,
                account_type="real_estate",
                initial_balance=Decimal("300000.00")
            )
            db.session.add(house)
            db.session.commit()

            # Add balance history (house appreciated)
            entry = AccountBalanceHistory(
                account_id=house.id,
                balance=350000.00,
                as_of_date=date(2025, 1, 1)
            )
            db.session.add(entry)
            db.session.commit()

            result = get_net_worth_summary(user)

            # Should use balance history value, not initial
            assert result['summary']['real_estate']['total'] == 350000.00
