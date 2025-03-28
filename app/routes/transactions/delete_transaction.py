from flask import redirect, url_for, flash, current_app
from flask_login import login_required
from app.routes.transactions import transactions_bp
from app.services.transactions.delete_transaction import get_transaction_by_id, delete_transaction_from_db
from sqlalchemy.exc import SQLAlchemyError


@transactions_bp.route("/transactions/delete/<int:transaction_id>", methods=["POST"])
@login_required
def delete_transaction(transaction_id):
    try:
        transaction = get_transaction_by_id(transaction_id)
        if not transaction:
            flash("Transaction not found or access denied.", "error")
            return redirect(url_for("transactions.transactions"))
        delete_transaction_from_db(transaction)
        flash("Transaction deleted successfully.", "success")
    except SQLAlchemyError as e:
        current_app.logger.error("Database error while deleting transaction ID %d: %s", transaction_id, str(e))
        flash("An error occurred while deleting the transaction. Please try again.", "error")
    except Exception as e:
        current_app.logger.error("Unexpected error while deleting transaction ID %d: %s", transaction_id, str(e))
        flash("An unexpected error occurred. Please try again.", "error")
    return redirect(url_for("transactions.transactions"))
