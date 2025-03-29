import calendar
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from sqlalchemy import extract, func
from flask import current_app
from app import db
from app.models.transaction import Transaction
from app.models.user import User
from app.models.category import Category
from app.models.account_type import AccountType


def get_date_range(today, time_filter, start_date_str=None, end_date_str=None):
    """
    Determine the start and end dates based on the time filter or custom date range.
    """
    current_app.logger.debug("Calculating date range with time_filter: %s, start_date_str: %s, end_date_str: %s",
                             time_filter, start_date_str, end_date_str)
    if time_filter == 'custom':
        start_date, end_date = parse_custom_date_range(today, start_date_str, end_date_str)
        current_app.logger.debug("Custom date range computed: %s to %s", start_date, end_date)
    elif time_filter == 'year':
        start_date = (today - relativedelta(months=12)).replace(day=1)
        end_date = today
        current_app.logger.debug("Year filter date range computed: %s to %s", start_date, end_date)
    elif time_filter == 'ytd':
        start_date = date(today.year, 1, 1)
        end_date = today
        current_app.logger.debug("YTD date range computed: %s to %s", start_date, end_date)
    else:
        # Default fallback: last 12 months
        start_date = today - relativedelta(months=12)
        end_date = today
        current_app.logger.debug("Default date range computed: %s to %s", start_date, end_date)
    return start_date, end_date


def parse_custom_date_range(today, start_date_str, end_date_str):
    """
    Parse custom start and end dates from request arguments.
    """
    start_date = None
    end_date = None

    # Parse start_date
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            current_app.logger.debug("Parsed custom start_date: %s", start_date)
        except ValueError as e:
            current_app.logger.error("Error parsing custom start_date '%s': %s", start_date_str, e)
    else:
        current_app.logger.debug("No custom start_date provided.")

    # Parse end_date
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            current_app.logger.debug("Parsed custom end_date: %s", end_date)
        except ValueError as e:
            current_app.logger.error("Error parsing custom end_date '%s': %s", end_date_str, e)
    else:
        current_app.logger.debug("No custom end_date provided.")

    # Fallback logic if dates are missing or invalid
    if not start_date:
        start_date = today - relativedelta(months=12)
        current_app.logger.debug("Fallback start_date used: %s", start_date)
    if not end_date:
        end_date = today
        current_app.logger.debug("Fallback end_date used: %s", end_date)

    return start_date, end_date


def get_family_filter(current_user):
    """
    Build the family filter for transactions based on the current user.
    """
    if current_user.family_id:
        current_app.logger.debug("Building family filter for family_id: %s", current_user.family_id)
        return Transaction.user.has(User.family_id == current_user.family_id)
    else:
        current_app.logger.debug("User %s has no family_id; filtering by user_id.", current_user.id)
        return Transaction.user_id == current_user.id


def build_base_query(family_filter, start_date, end_date, category_id=None, account_id=None):
    """
    Build the base query for transactions within the specified date range.
    """
    current_app.logger.debug("Building base query with start_date: %s, end_date: %s, category_id: %s, account_id: %s",
                             start_date, end_date, category_id, account_id)
    query = db.session.query(Transaction).filter(
        family_filter,
        Transaction.is_transfer.is_(False),
        Transaction.timestamp >= start_date,
        Transaction.timestamp <= end_date
    )
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
        current_app.logger.debug("Added category filter: %s", category_id)
    if account_id:
        query = query.filter(Transaction.account_id == account_id)
        current_app.logger.debug("Added account filter: %s", account_id)
    return query


def generate_chart_data(family_filter, start_date, end_date, category_id=None, account_id=None):
    """
    Generate chart data for the monthly spending report (only negative amounts).
    """
    current_app.logger.debug("Generating chart data with family_filter: %s, start_date: %s, end_date: %s, category_id: %s, account_id: %s",
                             family_filter, start_date, end_date, category_id, account_id)
    chart_query = db.session.query(
        extract('year', Transaction.timestamp).label('year'),
        extract('month', Transaction.timestamp).label('month'),
        func.sum(Transaction.amount).label('total')
    ).filter(
        family_filter,
        Transaction.amount < 0,
        Transaction.is_transfer.is_(False),
        Transaction.timestamp >= start_date,
        Transaction.timestamp <= end_date
    )
    if category_id:
        chart_query = chart_query.filter(Transaction.category_id == category_id)
        current_app.logger.debug("Added category filter to chart_query: %s", category_id)
    if account_id:
        chart_query = chart_query.filter(Transaction.account_id == account_id)
        current_app.logger.debug("Added account filter to chart_query: %s", account_id)

    chart_query = chart_query.group_by('year', 'month').order_by('year', 'month')
    current_app.logger.debug("Final chart query: %s", chart_query)
    results = chart_query.all()
    current_app.logger.debug("Chart query returned %d rows", len(results))
    sorted_results = sorted(results, key=lambda r: (r.year, r.month))
    labels = []
    totals = []

    for row in sorted_results:
        label = f"{int(row.year)}-{int(row.month):02d} ({calendar.month_abbr[int(row.month)]})"
        labels.append(label)
        totals.append(abs(float(row.total)) if row.total else 0)
    current_app.logger.debug("Generated chart data - labels: %s, totals: %s", labels, totals)
    return labels, totals


def get_dropdown_options(current_user):
    """
    Retrieve dropdown options for categories and accounts (family-based).
    """
    current_app.logger.debug("Retrieving dropdown options for user: %s", current_user.id)
    if current_user.family_id:
        categories = Category.query.filter_by(family_id=current_user.family_id).all()
        accounts = AccountType.query.filter_by(family_id=current_user.family_id).all()
        current_app.logger.debug("Found %d categories and %d accounts for family_id: %s",
                                 len(categories), len(accounts), current_user.family_id)
    else:
        categories = []
        accounts = []
        current_app.logger.debug("User %s has no family_id; returning empty dropdown options.", current_user.id)
    return categories, accounts
