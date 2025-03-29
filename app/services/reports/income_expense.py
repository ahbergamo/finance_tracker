from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from sqlalchemy import extract, func, case
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app
from app import db
from app.models.transaction import Transaction
from app.models.user import User
from app.models.category import Category
from app.models.account_type import AccountType


def get_date_filters(request_args):
    """
    Retrieve and compute default values for start_date and end_date query parameters.
    """
    try:
        today = date.today()
        start_date = request_args.get('start_date')
        end_date = request_args.get('end_date')

        if not start_date:
            computed_start = today - relativedelta(months=12)
            start_date = computed_start.replace(day=1).strftime('%Y-%m-%d')
            current_app.logger.debug("Computed start_date: %s", start_date)
        if not end_date:
            first_of_this_month = today.replace(day=1)
            last_day_previous = first_of_this_month - relativedelta(days=1)
            end_date = last_day_previous.strftime('%Y-%m-%d')
            current_app.logger.debug("Computed end_date: %s", end_date)

        return start_date, end_date
    except Exception as e:
        current_app.logger.error("Error in get_date_filters: %s", e)
        today = date.today()
        computed_start = today - relativedelta(months=12)
        return computed_start.replace(day=1).strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')


def parse_date_range(start_date_str, end_date_str):
    """
    Parse start_date and end_date strings into datetime objects.
    """
    today = date.today()
    try:
        start_dt = datetime.strptime(start_date_str, '%Y-%m-%d')
        current_app.logger.debug("Parsed start_date: %s", start_dt)
    except ValueError as e:
        current_app.logger.error("Invalid start_date '%s': %s. Falling back to default.", start_date_str, e)
        computed_start = today - relativedelta(months=12)
        start_dt = computed_start.replace(day=1)
    try:
        end_dt = datetime.strptime(end_date_str, '%Y-%m-%d')
        current_app.logger.debug("Parsed end_date: %s", end_dt)
    except ValueError as e:
        current_app.logger.error("Invalid end_date '%s': %s. Falling back to default.", end_date_str, e)
        first_of_this_month = today.replace(day=1)
        end_dt = first_of_this_month - relativedelta(days=1)

    return start_dt, end_dt


def get_family_user_ids(current_user):
    """
    Retrieve the list of user IDs for the current user's family or the user alone.
    """
    try:
        if current_user.family_id:
            family_users = User.query.filter_by(family_id=current_user.family_id).all()
            user_ids = [u.id for u in family_users]
            current_app.logger.debug("Family user IDs: %s", user_ids)
            return user_ids
        else:
            current_app.logger.debug("User %s has no family_id, returning own ID.", current_user.id)
            return [current_user.id]
    except Exception as e:
        current_app.logger.error("Error in get_family_user_ids for user %s: %s", current_user.id, e)
        return [current_user.id]


def build_transaction_query(user_ids, start_dt, end_dt, category_id=None, account_id=None):
    """
    Build the SQLAlchemy query for transactions based on the provided filters.
    """
    try:
        query = db.session.query(Transaction).filter(
            Transaction.user_id.in_(user_ids),
            Transaction.is_transfer.is_(False),
            Transaction.timestamp >= start_dt,
            Transaction.timestamp <= end_dt
        )
        if category_id:
            query = query.filter(Transaction.category_id == category_id)
        if account_id:
            query = query.filter(Transaction.account_id == account_id)

        current_app.logger.debug(
            "Built transaction query with filters: user_ids=%s, start_dt=%s, end_dt=%s, category_id=%s, account_id=%s",
            user_ids, start_dt, end_dt, category_id, account_id
        )
        return query
    except Exception as e:
        current_app.logger.error("Error in build_transaction_query: %s", e)
        return db.session.query(Transaction).filter(False)  # return an empty query


def process_transaction_results(query):
    """
    Summarize the transaction query results into labels, incomes, and expenses per month.
    """
    try:
        results = query.with_entities(
            extract('year', Transaction.timestamp).label('year'),
            extract('month', Transaction.timestamp).label('month'),
            func.sum(case((Transaction.amount > 0, Transaction.amount), else_=0)).label('income'),
            func.sum(case((Transaction.amount < 0, Transaction.amount), else_=0)).label('expense')
        ).group_by('year', 'month').order_by('year', 'month').all()

        current_app.logger.debug("Raw transaction results: %s", results)
        sorted_results = sorted(results, key=lambda r: (r.year, r.month))
        labels = []
        incomes = []
        expenses = []

        for row in sorted_results:
            label = f"{int(row.year)}-{int(row.month):02d}"
            labels.append(label)
            incomes.append(float(row.income) if row.income else 0)
            expenses.append(abs(float(row.expense)) if row.expense else 0)

        current_app.logger.debug("Processed transaction results: labels=%s, incomes=%s, expenses=%s", labels, incomes, expenses)
        return labels, incomes, expenses
    except Exception as e:
        current_app.logger.error("Error in process_transaction_results: %s", e)
        return [], [], []


def get_cached_categories(current_user):
    """
    Retrieve and cache the list of categories for the current user's family.
    """
    try:
        categories = Category.query.filter_by(family_id=current_user.family_id).all()
        current_app.logger.debug("Loaded %d categories for family_id %s", len(categories), current_user.family_id)
        return categories
    except SQLAlchemyError as e:
        current_app.logger.error("Failed to load categories: %s", e)
        return []
    except Exception as e:
        current_app.logger.error("Unexpected error in get_cached_categories: %s", e)
        return []


def get_cached_accounts(current_user):
    """
    Retrieve and cache the list of accounts for the current user's family.
    """
    try:
        accounts = AccountType.query.filter_by(family_id=current_user.family_id).all()
        current_app.logger.debug("Loaded %d accounts for family_id %s", len(accounts), current_user.family_id)
        return accounts
    except SQLAlchemyError as e:
        current_app.logger.error("Failed to load accounts: %s", e)
        return []
    except Exception as e:
        current_app.logger.error("Unexpected error in get_cached_accounts: %s", e)
        return []
