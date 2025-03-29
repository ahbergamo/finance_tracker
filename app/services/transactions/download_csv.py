import csv
import io
from flask import Response, request, current_app
from datetime import datetime
from calendar import monthrange
from sqlalchemy.exc import SQLAlchemyError
from app.models.transaction import Transaction


def build_transaction_query(family_user_ids, filter_type, category_id, account_id):
    """
    Build a query to fetch transactions based on filters.
    """
    try:
        current_app.logger.debug("Building transaction query for family_user_ids: %s", family_user_ids)
        query = Transaction.query.filter(
            Transaction.user_id.in_(family_user_ids),
            Transaction.is_transfer.is_(False)
        )
        if category_id:
            current_app.logger.debug("Applying category filter: %s", category_id)
            query = query.filter(Transaction.category_id == category_id)
        if account_id:
            current_app.logger.debug("Applying account filter: %s", account_id)
            query = query.filter(Transaction.account_id == account_id)
        if filter_type == "income":
            current_app.logger.debug("Filtering for income transactions")
            query = query.filter(Transaction.amount > 0)
        elif filter_type == "expense":
            current_app.logger.debug("Filtering for expense transactions")
            query = query.filter(Transaction.amount < 0)
        return query
    except Exception as e:
        current_app.logger.error("Database error while building transaction query: %s", e)
        return Transaction.query.filter(False)


def apply_time_filter(query, time_filter):
    """
    Apply a time filter to the query.
    """
    now = datetime.now()
    try:
        if time_filter == "month":
            start_date = datetime(now.year, now.month, 1)
            last_day = monthrange(now.year, now.month)[1]
            end_date = datetime(now.year, now.month, last_day)
            query = query.filter(Transaction.timestamp >= start_date)
            current_app.logger.debug("Applied 'month' time filter: start_date=%s, end_date=%s", start_date, end_date)
        elif time_filter == "ytd":
            start_date = datetime(now.year, 1, 1)
            query = query.filter(Transaction.timestamp >= start_date)
            current_app.logger.debug("Applied 'ytd' time filter: start_date=%s", start_date)
        elif time_filter == "year":
            start_date = datetime(now.year, 1, 1)
            end_date = datetime(now.year, 12, 31)
            query = query.filter(Transaction.timestamp.between(start_date, end_date))
            current_app.logger.debug("Applied 'year' time filter: start_date=%s, end_date=%s", start_date, end_date)
        elif time_filter == "custom":
            start_date_str = request.args.get("start_date")
            end_date_str = request.args.get("end_date")
            if start_date_str and end_date_str:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
                query = query.filter(Transaction.timestamp.between(start_date, end_date))
                current_app.logger.debug("Applied 'custom' time filter: start_date=%s, end_date=%s", start_date, end_date)
            else:
                current_app.logger.warning("Custom time filter selected but start_date or end_date missing")
        return query
    except Exception as e:
        current_app.logger.error("Error applying time filter: %s", e)
        return query


def fetch_transactions(query):
    """
    Execute the query and return all transactions.
    """
    try:
        transactions = query.order_by(Transaction.timestamp.desc()).all()
        current_app.logger.debug("Fetched %d transactions", len(transactions))
        return transactions
    except SQLAlchemyError as e:
        current_app.logger.error("Database error while fetching transactions: %s", e)
        return []


def generate_csv_response(transactions):
    """
    Generate and return a CSV Response from the transactions list.
    """
    try:
        current_app.logger.debug("Generating CSV response for %d transactions", len(transactions))
        si = io.StringIO()
        writer = csv.writer(si)
        writer.writerow(["Date", "Description", "Amount", "Account Type", "Category"])
        for tx in transactions:
            tx_date = tx.timestamp.strftime("%Y-%m-%d") if tx.timestamp else ""
            category = tx.category.name if tx.category else "Uncategorized"
            account_name = tx.account.name if hasattr(tx, "account") and tx.account and tx.account.name else ""
            writer.writerow([tx_date, tx.description, f"{tx.amount:.2f}", account_name, category])
        output = si.getvalue()
        si.close()
        headers = {
            "Content-Disposition": "attachment; filename=transactions.csv",
            "Content-type": "text/csv"
        }
        current_app.logger.debug("CSV response generated successfully")
        return Response(output, headers=headers)
    except Exception as e:
        current_app.logger.error("Error generating CSV response: %s", e)
        return Response("Error generating CSV", status=500)
