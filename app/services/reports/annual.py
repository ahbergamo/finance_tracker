from datetime import datetime
from sqlalchemy import extract, func, case
from flask import current_app
from app import db
from app.models.transaction import Transaction
from app.models.user import User
from app.models.category import Category
from app.models.account_type import AccountType


def parse_filters(request_args) -> dict:
    """
    Parse and validate query parameters for filtering.
    """
    filters = {}
    filters['start_date'] = request_args.get('start_date')
    filters['end_date'] = request_args.get('end_date')
    filters['category_id'] = request_args.get('category_id', type=int)
    filters['account_id'] = request_args.get('account_id', type=int)
    current_app.logger.debug("Parsed filters: %s", filters)
    return filters


def get_family_user_ids(current_user: User) -> list:
    """
    Retrieve the IDs of all users in the same family as the current user.
    """
    try:
        if current_user.family_id:
            family_user_ids = User.query.with_entities(User.id)\
                .filter_by(family_id=current_user.family_id).all()
            user_ids = [user_id[0] for user_id in family_user_ids]  # Extract IDs from tuples
            current_app.logger.debug("Retrieved family user IDs for family_id %s: %s", current_user.family_id, user_ids)
            return user_ids
        else:
            current_app.logger.debug("User %s does not belong to a family; using their own ID.", current_user.id)
            return [current_user.id]
    except Exception as e:
        current_app.logger.error("Error retrieving family user IDs for user %s: %s", current_user.id, e)
        return [current_user.id]


def build_query(filters: dict, family_user_ids: list, current_user: User):
    """
    Build the SQLAlchemy query for the annual overview report.
    Returns None if there's any invalid date format.
    """
    try:
        income_sum = func.sum(case((Transaction.amount > 0, Transaction.amount), else_=0))
        expense_sum = func.sum(case((Transaction.amount < 0, Transaction.amount), else_=0))

        query = db.session.query(
            extract('year', Transaction.timestamp).label('year'),
            income_sum.label('total_income'),
            expense_sum.label('total_expense')
        ).filter(
            Transaction.user_id.in_(family_user_ids),
            Transaction.is_transfer.is_(False)
        )

        # Validate and apply date filters
        if filters['start_date']:
            try:
                start_dt = datetime.strptime(filters['start_date'], '%Y-%m-%d')
                query = query.filter(Transaction.timestamp >= start_dt)
                current_app.logger.debug("Applied start_date filter: %s", start_dt)
            except ValueError as e:
                current_app.logger.error("Invalid start_date format: %s for user %s. Error: %s", filters['start_date'], current_user.id, e)
                return None

        if filters['end_date']:
            try:
                end_dt = datetime.strptime(filters['end_date'], '%Y-%m-%d')
                query = query.filter(Transaction.timestamp <= end_dt)
                current_app.logger.debug("Applied end_date filter: %s", end_dt)
            except ValueError as e:
                current_app.logger.error("Invalid end_date format: %s for user %s. Error: %s", filters['end_date'], current_user.id, e)
                return None

        if filters['category_id']:
            query = query.filter(Transaction.category_id == filters['category_id'])
            current_app.logger.debug("Applied category filter: %s", filters['category_id'])
        if filters['account_id']:
            query = query.filter(Transaction.account_id == filters['account_id'])
            current_app.logger.debug("Applied account filter: %s", filters['account_id'])

        query = query.group_by('year').order_by('year')
        current_app.logger.debug("Built query: %s", query)
        return query
    except Exception as e:
        current_app.logger.error("Error building query for user %s: %s", current_user.id, e)
        return None


def get_dropdown_options(current_user: User) -> tuple:
    """
    Retrieve dropdown options for categories and accounts.
    """
    try:
        if current_user.family_id:
            filter_field = 'family_id'
            filter_value = current_user.family_id
        else:
            filter_field = 'user_id'
            filter_value = current_user.id

        categories = Category.query.filter_by(**{filter_field: filter_value}).all()
        accounts = AccountType.query.filter_by(**{filter_field: filter_value}).all()
        current_app.logger.debug("Retrieved %d categories and %d accounts for %s=%s",
                                 len(categories), len(accounts), filter_field, filter_value)
        return categories, accounts
    except Exception as e:
        current_app.logger.error("Error retrieving dropdown options for user %s: %s", current_user.id, e)
        return ([], [])
