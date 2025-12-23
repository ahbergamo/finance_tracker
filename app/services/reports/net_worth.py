from datetime import date
from dateutil.relativedelta import relativedelta
from sqlalchemy import func
from app import db
from app.models.transaction import Transaction
from app.models.user import User
from app.models.account import Account
from app.models.account_balance_history import AccountBalanceHistory


def get_family_user_ids(current_user):
    """Get all user IDs for the current user's family."""
    if current_user.family_id:
        users = User.query.filter_by(family_id=current_user.family_id).all()
        return [u.id for u in users]
    return [current_user.id]


def get_transaction_based_balance(account, user_ids, as_of_date=None):
    """
    Calculate balance for transaction-based accounts (checking, savings, credit_card).
    Balance = initial_balance + sum of all transactions up to as_of_date.
    """
    query = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.account_id == account.id,
        Transaction.user_id.in_(user_ids)
    )
    if as_of_date:
        query = query.filter(Transaction.timestamp <= as_of_date)

    transaction_total = query.scalar() or 0
    initial = float(account.initial_balance or 0)
    return initial + float(transaction_total)


# Account types that use balance history instead of transactions
BALANCE_HISTORY_TYPES = ('retirement', 'brokerage', 'real_estate', 'vehicle', 'other_asset', 'loan')

# Account types that are always liabilities (negative balances)
LIABILITY_TYPES = ('loan',)


def get_balance_history_balance(account, as_of_date=None):
    """
    Get balance for balance-history accounts (retirement, brokerage, real_estate, etc.).
    Returns the most recent balance entry on or before as_of_date,
    or initial_balance if no history exists.
    """
    query = AccountBalanceHistory.query.filter_by(account_id=account.id)
    if as_of_date:
        query = query.filter(AccountBalanceHistory.as_of_date <= as_of_date)

    latest = query.order_by(AccountBalanceHistory.as_of_date.desc()).first()
    if latest:
        return float(latest.balance)
    return float(account.initial_balance or 0)


def get_account_balance(account, user_ids, as_of_date=None):
    """Get balance for any account type."""
    # Pensions use present value calculation, not balance history
    if account.is_pension():
        return float(account.get_pension_present_value())

    if account.account_type in BALANCE_HISTORY_TYPES:
        return get_balance_history_balance(account, as_of_date)
    else:
        return get_transaction_based_balance(account, user_ids, as_of_date)


def get_net_worth_summary(current_user):
    """
    Calculate net worth summary with all accounts grouped by type.
    Returns dict with account details and totals.
    """
    user_ids = get_family_user_ids(current_user)
    accounts = Account.query.filter_by(family_id=current_user.family_id).all()

    summary = {
        'checking': {'accounts': [], 'total': 0},
        'savings': {'accounts': [], 'total': 0},
        'credit_card': {'accounts': [], 'total': 0},
        'retirement': {'accounts': [], 'total': 0},
        'brokerage': {'accounts': [], 'total': 0},
        'real_estate': {'accounts': [], 'total': 0},
        'vehicle': {'accounts': [], 'total': 0},
        'other_asset': {'accounts': [], 'total': 0},
        'loan': {'accounts': [], 'total': 0},
    }

    total_assets = 0
    total_liabilities = 0

    for account in accounts:
        balance = get_account_balance(account, user_ids)
        account_type = account.account_type or 'checking'

        account_data = {
            'id': account.id,
            'name': account.name,
            'balance': balance,
            'retirement_type': account.retirement_type,
            'is_pension': account.is_pension(),
            'pension_monthly_benefit': float(account.pension_monthly_benefit) if account.pension_monthly_benefit else None,
            'pension_start_date': account.pension_start_date
        }

        if account_type in summary:
            summary[account_type]['accounts'].append(account_data)
            summary[account_type]['total'] += balance

        # Determine if asset or liability
        if account_type in LIABILITY_TYPES:
            # Loans are always liabilities (store as positive, count as liability)
            total_liabilities += abs(balance)
        elif account_type == 'credit_card':
            # Credit cards with negative balance are liabilities
            if balance < 0:
                total_liabilities += abs(balance)
            else:
                total_assets += balance
        else:
            # All other accounts: positive = asset, negative = liability
            if balance >= 0:
                total_assets += balance
            else:
                total_liabilities += abs(balance)

    return {
        'summary': summary,
        'total_assets': total_assets,
        'total_liabilities': total_liabilities,
        'net_worth': total_assets - total_liabilities
    }


def get_net_worth_history(current_user, months=12):
    """
    Calculate net worth over time for charting.
    Returns labels and data points for the last N months.
    """
    user_ids = get_family_user_ids(current_user)
    accounts = Account.query.filter_by(family_id=current_user.family_id).all()

    today = date.today()
    labels = []
    net_worth_data = []
    assets_data = []
    liabilities_data = []

    # Go back N months
    for i in range(months - 1, -1, -1):
        target_date = today - relativedelta(months=i)
        # Use last day of month for historical, today for current
        if i > 0:
            # Last day of that month
            next_month = target_date.replace(day=28) + relativedelta(days=4)
            target_date = next_month - relativedelta(days=next_month.day)

        total_assets = 0
        total_liabilities = 0

        for account in accounts:
            balance = get_account_balance(account, user_ids, target_date)
            account_type = account.account_type or 'checking'

            if account_type in LIABILITY_TYPES:
                total_liabilities += abs(balance)
            elif account_type == 'credit_card':
                if balance < 0:
                    total_liabilities += abs(balance)
                else:
                    total_assets += balance
            else:
                if balance >= 0:
                    total_assets += balance
                else:
                    total_liabilities += abs(balance)

        labels.append(target_date.strftime('%b %Y'))
        net_worth_data.append(total_assets - total_liabilities)
        assets_data.append(total_assets)
        liabilities_data.append(total_liabilities)

    return {
        'labels': labels,
        'net_worth': net_worth_data,
        'assets': assets_data,
        'liabilities': liabilities_data
    }
