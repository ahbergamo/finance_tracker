from flask import current_app, request
from flask_login import current_user
from sqlalchemy import func, case, and_
from datetime import datetime
from calendar import monthrange
from app import db
from app.models.transaction import Transaction
from app.models.category import Category
from app.models.account_type import AccountType
from app.services.transactions.utilities import get_family_user_ids


def apply_time_filter(query, time_filter):
    now = datetime.now()
    try:
        current_app.logger.debug("Applying time filter: %s", time_filter)
        if time_filter == "month":
            start_date = datetime(now.year, now.month, 1)
            last_day = monthrange(now.year, now.month)[1]
            end_date = datetime(now.year, now.month, last_day)
            query = query.filter(Transaction.timestamp >= start_date)
            date_range_display = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        elif time_filter == "ytd":
            start_date = datetime(now.year, 1, 1)
            query = query.filter(Transaction.timestamp >= start_date)
            date_range_display = f"{start_date.strftime('%Y-%m-%d')} to {now.strftime('%Y-%m-%d')}"
        elif time_filter == "year":
            start_date = datetime(now.year, 1, 1)
            end_date = datetime(now.year, 12, 31)
            query = query.filter(Transaction.timestamp.between(start_date, end_date))
            date_range_display = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        elif time_filter == "custom":
            start_date_str = request.args.get("start_date")
            end_date_str = request.args.get("end_date")
            current_app.logger.debug("Custom time filter with start_date: %s, end_date: %s", start_date_str, end_date_str)
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            query = query.filter(Transaction.timestamp.between(start_date, end_date))
            date_range_display = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        else:
            date_range_display = "All Time"
        current_app.logger.debug("Time filter applied, date range: %s", date_range_display)
    except Exception as e:
        current_app.logger.error("Error applying time filter: %s", e)
        date_range_display = "Invalid date range"
    return query, date_range_display


def calculate_summary(query):
    try:
        current_app.logger.debug("Calculating summary for query")
        return query.with_entities(
            func.count(Transaction.id).label("total_count"),
            func.coalesce(func.sum(case((Transaction.amount > 0, Transaction.amount), else_=0)), 0).label("total_income"),
            func.coalesce(func.sum(case((Transaction.amount < 0, Transaction.amount), else_=0)), 0).label("total_expense")
        ).first()
    except Exception as e:
        current_app.logger.error("Error calculating summary: %s", e)
        return None


def apply_filters(query, category_id, category_ids, account_id):
    try:
        current_app.logger.debug("Applying filters with category_id: %s, category_ids: %s, account_id: %s",
                                 category_id, category_ids, account_id)
        if category_ids:
            query = query.filter(Transaction.category_id.in_(category_ids))
        elif category_id:
            query = query.filter(Transaction.category_id == category_id)
        if account_id:
            query = query.filter(Transaction.account_id == account_id)
    except Exception as e:
        current_app.logger.error("Error applying filters: %s", e)
    return query


def handle_duplicates(query, family_user_ids, category_id, category_ids, account_id):
    from app.models.transaction import Transaction  # local import
    try:
        current_app.logger.debug("Handling duplicates with family_user_ids: %s, category_id: %s, category_ids: %s, account_id: %s",
                                 family_user_ids, category_id, category_ids, account_id)
        subq = db.session.query(
            func.date(Transaction.timestamp).label('dup_date'),
            Transaction.amount.label('dup_amount')
        ).filter(Transaction.user_id.in_(family_user_ids)).group_by(
            func.date(Transaction.timestamp),
            Transaction.amount
        ).having(func.count(Transaction.id) > 1).subquery()

        duplicate_transactions_query = Transaction.query.join(
            subq,
            and_(
                func.date(Transaction.timestamp) == subq.c.dup_date,
                Transaction.amount == subq.c.dup_amount
            )
        ).filter(Transaction.user_id.in_(family_user_ids))
        duplicate_transactions_query = apply_filters(duplicate_transactions_query, category_id, category_ids, account_id)
        duplicate_transactions = duplicate_transactions_query.all()
        current_app.logger.debug("Found %d duplicate transactions", len(duplicate_transactions))
        grouped_duplicates = {}
        for tx in duplicate_transactions:
            key = (tx.timestamp.strftime('%Y-%m-%d'), tx.amount)
            grouped_duplicates.setdefault(key, []).append(tx)
        summary = calculate_summary(duplicate_transactions_query)
        current_app.logger.debug("Calculated duplicate transactions summary: %s", summary)
        return grouped_duplicates, summary
    except Exception as e:
        current_app.logger.error("Error handling duplicates: %s", e)
        return {}, None


def process_transactions_view(filter_type, time_filter, category_id, category_ids, account_id, page, per_page):
    current_app.logger.debug("Processing transactions view with filter_type: %s, time_filter: %s, category_id: %s, category_ids: %s, account_id: %s, page: %s, per_page: %s",
                             filter_type, time_filter, category_id, category_ids, account_id, page, per_page)
    family_user_ids = get_family_user_ids()
    if filter_type == "transfers":
        current_app.logger.debug("Filtering for transfers")
        query = Transaction.query.filter(
            Transaction.user_id.in_(family_user_ids),
            Transaction.is_transfer.is_(True)
        )
        date_range_display = "Transfer Transactions"
    else:
        query = Transaction.query.filter(
            Transaction.user_id.in_(family_user_ids),
            Transaction.is_transfer.is_(False)
        )
    query = apply_filters(query, category_id, category_ids, account_id)
    if filter_type == "duplicates":
        current_app.logger.debug("Processing duplicates view")
        grouped_duplicates, summary = handle_duplicates(query, family_user_ids, category_id, category_ids, account_id)
        account_types = AccountType.query.filter_by(family_id=current_user.family_id).all()
        current_app.logger.debug("Returning duplicates view with %d duplicate groups", len(grouped_duplicates))
        return {
            "grouped_duplicates": grouped_duplicates,
            "account_types": account_types,
            "selected_account": account_id,
            "categories": Category.query.all(),
            "selected_category": category_id,
            "filter_type": filter_type,
            "time_filter": time_filter,
            "pagination": None,
            "date_range_display": "Duplicate Transactions",
            "summary": summary,
        }
    else:
        if filter_type == "income":
            current_app.logger.debug("Filtering income transactions")
            query = query.filter(Transaction.amount > 0)
        elif filter_type == "expense":
            current_app.logger.debug("Filtering expense transactions")
            query = query.filter(Transaction.amount < 0)
        query, date_range_display = apply_time_filter(query, time_filter)
        query = query.order_by(Transaction.timestamp.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        user_transactions = pagination.items
        summary = calculate_summary(query)
        account_types = AccountType.query.filter_by(family_id=current_user.family_id).all()
        current_app.logger.debug("Processed transactions view: %d transactions, date_range_display: %s", len(user_transactions), date_range_display)
        return {
            "transactions": user_transactions,
            "account_types": account_types,
            "selected_account": account_id,
            "categories": Category.query.all(),
            "selected_category": category_id,
            "filter_type": filter_type,
            "time_filter": time_filter,
            "pagination": pagination,
            "date_range_display": date_range_display,
            "summary": summary,
        }
