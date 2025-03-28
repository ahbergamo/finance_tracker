from flask import current_app
from app import db
from app.models.transaction import Transaction
from app.services.transactions.utilities import get_family_user_ids
from flask_login import current_user


def get_transaction_by_id(transaction_id):
    """
    Fetch a transaction by its ID ensuring it belongs to the current user/family.
    """
    current_app.logger.debug("Fetching transaction by id: %s for user: %s", transaction_id, current_user.id)
    try:
        transaction = Transaction.query.filter(
            Transaction.id == transaction_id,
            Transaction.user_id.in_(get_family_user_ids())
        ).first()
        if transaction:
            current_app.logger.debug("Found transaction: %s", transaction)
        else:
            current_app.logger.warning("Transaction not found for id: %s for user: %s", transaction_id, current_user.id)
        return transaction
    except Exception as e:
        current_app.logger.error("Error fetching transaction by id %s for user %s: %s", transaction_id, current_user.id, str(e))
        return None


def delete_transaction_from_db(transaction):
    """
    Delete the provided transaction from the database.
    """
    current_app.logger.debug("Attempting to delete transaction: %s", transaction)
    try:
        db.session.delete(transaction)
        db.session.commit()
        current_app.logger.info("Deleted transaction ID %d for user %s", transaction.id, current_user.id)
    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Error deleting transaction ID %s for user %s: %s", transaction.id, current_user.id, str(e))
