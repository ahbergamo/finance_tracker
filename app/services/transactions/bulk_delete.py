from flask import flash, redirect, url_for, render_template, request, current_app
from flask_login import current_user
from app import db
from app.models.transaction import Transaction
from app.models.category import Category
from app.models.account_type import AccountType
from app.services.transactions.utilities import apply_date_filter


def build_transaction_query(family_user_ids):
    """
    Build the base query for filtering transactions and extract filter values.
    """
    current_app.logger.debug("Building transaction query for family_user_ids: %s", family_user_ids)
    query = Transaction.query.filter(Transaction.user_id.in_(family_user_ids))
    filters = {
        "start_date": request.args.get("start_date"),
        "end_date": request.args.get("end_date"),
        "category_id": request.args.get("category_id", type=int),
        "account_id": request.args.get("account_id", type=int),
    }
    current_app.logger.debug("Extracted filters: %s", filters)
    if filters["start_date"]:
        current_app.logger.debug("Applying start_date filter: %s", filters["start_date"])
        query = apply_date_filter(query, filters["start_date"], "start")
    if filters["end_date"]:
        current_app.logger.debug("Applying end_date filter: %s", filters["end_date"])
        query = apply_date_filter(query, filters["end_date"], "end")
    if filters["category_id"]:
        current_app.logger.debug("Applying category filter: %s", filters["category_id"])
        query = query.filter(Transaction.category_id == filters["category_id"])
    if filters["account_id"]:
        current_app.logger.debug("Applying account filter: %s", filters["account_id"])
        query = query.filter(Transaction.account_id == filters["account_id"])
    current_app.logger.debug("Built query: %s", query)
    return query, filters


def delete_all_transactions(query):
    """
    Delete all transactions matching the query.
    """
    try:
        current_app.logger.debug("Attempting to delete transactions with query: %s", query)
        count = query.delete(synchronize_session="fetch")
        db.session.commit()
        current_app.logger.info("Deleted %d transactions matching the query.", count)
        flash(f"Deleted all {count} matching transactions.", "success")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Error deleting all transactions: %s", str(e))
        flash("Error deleting transactions.", "danger")
    return redirect(url_for("transactions.bulk_delete"))


def delete_selected_transactions(filters):
    """
    Delete transactions selected by the user.
    """
    selected_ids = request.form.getlist("transaction_ids")
    current_app.logger.debug("Selected transaction IDs for deletion: %s", selected_ids)
    if selected_ids:
        try:
            count = Transaction.query.filter(Transaction.id.in_(selected_ids)).delete(synchronize_session="fetch")
            db.session.commit()
            current_app.logger.info("Deleted %d selected transactions.", count)
            flash(f"Deleted {count} transactions.", "success")
        except Exception as e:
            db.session.rollback()
            current_app.logger.error("Error deleting selected transactions: %s", str(e))
            flash("Error deleting selected transactions.", "danger")
    else:
        current_app.logger.warning("No transactions were selected for deletion.")
        flash("No transactions were selected.", "warning")
    return redirect(url_for("transactions.bulk_delete", **filters))


def handle_post_request(query, filters):
    """
    Process the POST request for bulk deletion.
    """
    current_app.logger.debug("Handling POST request for bulk deletion with filters: %s", filters)
    if request.form.get("delete_all"):
        current_app.logger.debug("Bulk delete triggered for all transactions")
        return delete_all_transactions(query)
    else:
        current_app.logger.debug("Bulk delete triggered for selected transactions")
        return delete_selected_transactions(filters)


def render_bulk_delete_page(query, filters):
    """
    Render the bulk deletion page with pagination and filter data.
    """
    current_app.logger.debug("Rendering bulk delete page with filters: %s", filters)
    page = request.args.get('page', 1, type=int)
    per_page = 20  # Adjust as needed
    try:
        pagination = query.order_by(Transaction.timestamp.desc()).paginate(page=page, per_page=per_page, error_out=False)
        transactions = pagination.items
        current_app.logger.debug("Retrieved %d transactions for page %d", len(transactions), page)
        categories = Category.query.filter_by(family_id=current_user.family_id).order_by(Category.name.asc()).all()
        account_types = AccountType.query.filter_by(family_id=current_user.family_id).order_by(AccountType.name.asc()).all()
        current_app.logger.debug("Retrieved %d categories and %d account types for family_id %s",
                                 len(categories), len(account_types), current_user.family_id)
    except Exception as e:
        current_app.logger.error("Error retrieving bulk delete page data: %s", str(e))
        flash("Error retrieving data.", "danger")
        transactions, categories, account_types, pagination = [], [], [], None

    return render_template(
        "transactions/bulk_delete.html",
        transactions=transactions,
        categories=categories,
        account_types=account_types,
        start_date=filters["start_date"],
        end_date=filters["end_date"],
        selected_category=filters["category_id"],
        selected_account=filters["account_id"],
        pagination=pagination,
    )
