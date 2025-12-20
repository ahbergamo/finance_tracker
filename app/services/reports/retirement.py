import calendar
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from sqlalchemy import extract, func, or_
from app import db
from app.models.transaction import Transaction
from app.models.user import User
from app.models.category import Category
from app.models.account_type import AccountType


def get_retirement_accounts(family_id):
    """Get all retirement account types for a family."""
    retirement_account_names = [
        '401k Account', 'Traditional IRA', 'Roth IRA', '403b Account'
    ]
    return AccountType.query.filter(
        AccountType.family_id == family_id,
        AccountType.name.in_(retirement_account_names)
    ).all()


def get_retirement_categories(family_id):
    """Get all retirement categories for a family."""
    retirement_category_names = [
        '401k Contribution', '401k Employer Match', 'Traditional IRA Contribution',
        'Roth IRA Contribution', '403b Contribution', '403b Employer Match',
        'HSA Contribution', 'Retirement Account Transfer', 'Retirement Investment',
        'Retirement Withdrawal'
    ]
    return Category.query.filter(
        Category.family_id == family_id,
        Category.name.in_(retirement_category_names)
    ).all()


def get_retirement_summary(current_user, start_date, end_date):
    """Generate retirement account summary data."""
    family_filter = get_family_filter(current_user)

    # Get retirement accounts and categories
    retirement_accounts = get_retirement_accounts(current_user.family_id)
    retirement_categories = get_retirement_categories(current_user.family_id)

    account_ids = [acc.id for acc in retirement_accounts]
    category_ids = [cat.id for cat in retirement_categories]

    # Query transactions from retirement accounts OR retirement categories
    query = db.session.query(Transaction).filter(
        family_filter,
        Transaction.timestamp >= start_date,
        Transaction.timestamp <= end_date,
        or_(
            Transaction.account_id.in_(account_ids),
            Transaction.category_id.in_(category_ids)
        )
    )

    transactions = query.all()

    # Group by account and category
    summary = {}
    total_contributions = 0
    total_withdrawals = 0

    for transaction in transactions:
        account_name = transaction.account.name
        category_name = transaction.category.name

        if account_name not in summary:
            summary[account_name] = {
                'categories': {},
                'total': 0
            }

        if category_name not in summary[account_name]['categories']:
            summary[account_name]['categories'][category_name] = 0

        summary[account_name]['categories'][category_name] += transaction.amount
        summary[account_name]['total'] += transaction.amount

        # Track contributions vs withdrawals
        if transaction.amount > 0:
            total_contributions += transaction.amount
        else:
            total_withdrawals += abs(transaction.amount)

    return {
        'summary': summary,
        'total_contributions': total_contributions,
        'total_withdrawals': total_withdrawals,
        'net_change': total_contributions - total_withdrawals
    }


def get_retirement_chart_data(current_user, start_date, end_date):
    """Generate chart data for retirement contributions over time."""
    family_filter = get_family_filter(current_user)

    retirement_accounts = get_retirement_accounts(current_user.family_id)
    retirement_categories = get_retirement_categories(current_user.family_id)

    account_ids = [acc.id for acc in retirement_accounts]
    category_ids = [cat.id for cat in retirement_categories]

    # Query monthly retirement activity
    chart_query = db.session.query(
        extract('year', Transaction.timestamp).label('year'),
        extract('month', Transaction.timestamp).label('month'),
        func.sum(Transaction.amount).label('total')
    ).filter(
        family_filter,
        Transaction.timestamp >= start_date,
        Transaction.timestamp <= end_date,
        or_(
            Transaction.account_id.in_(account_ids),
            Transaction.category_id.in_(category_ids)
        )
    ).group_by('year', 'month').order_by('year', 'month')

    results = chart_query.all()

    labels = []
    totals = []

    for row in results:
        label = f"{int(row.year)}-{int(row.month):02d} ({calendar.month_abbr[int(row.month)]})"
        labels.append(label)
        totals.append(float(row.total) if row.total else 0)

    return labels, totals


def get_retirement_account_balances(current_user, end_date):
    """Calculate retirement account balances up to end_date."""
    family_filter = get_family_filter(current_user)
    retirement_accounts = get_retirement_accounts(current_user.family_id)

    balances = {}

    for account in retirement_accounts:
        # Sum all transactions for this account up to end_date
        total = db.session.query(func.sum(Transaction.amount)).filter(
            family_filter,
            Transaction.account_id == account.id,
            Transaction.timestamp <= end_date
        ).scalar() or 0

        balances[account.name] = total

    return balances


def get_family_filter(current_user):
    """Build the family filter for transactions based on the current user."""
    if current_user.family_id:
        return Transaction.user.has(User.family_id == current_user.family_id)
    else:
        return Transaction.user_id == current_user.id


def get_date_range(today, time_filter, start_date_str=None, end_date_str=None):
    """Determine the start and end dates based on the time filter or custom date range."""
    if time_filter == 'custom':
        start_date, end_date = parse_custom_date_range(today, start_date_str, end_date_str)
    elif time_filter == 'year':
        start_date = (today - relativedelta(months=12)).replace(day=1)
        end_date = today
    elif time_filter == 'ytd':
        start_date = date(today.year, 1, 1)
        end_date = today
    else:
        # Default fallback: last 12 months
        start_date = today - relativedelta(months=12)
        end_date = today
    return start_date, end_date


def parse_custom_date_range(today, start_date_str, end_date_str):
    """Parse custom start and end dates from request arguments."""
    start_date = None
    end_date = None

    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    if not start_date:
        start_date = today - relativedelta(months=12)
    if not end_date:
        end_date = today

    return start_date, end_date
