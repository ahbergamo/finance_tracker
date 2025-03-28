from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models.transaction import Transaction
from app.models.category import Category
from app.models.account_type import AccountType
from app.routes.transactions import transactions_bp
from app.services.transactions.utilities import get_family_user_ids


@transactions_bp.route("/transactions/edit/<int:transaction_id>", methods=["GET", "POST"])
@login_required
def edit_transaction(transaction_id):
    """
    Route to edit an existing transaction. Handles both GET and POST requests.
    """
    try:
        transaction = get_transaction(transaction_id)
    except Exception as e:
        current_app.logger.error("Error fetching transaction ID %d: %s", transaction_id, str(e))
        flash("An error occurred while fetching the transaction.", "danger")
        return redirect(url_for("transactions.transactions"))

    if request.method == "POST":
        return handle_transaction_update(transaction)

    return render_edit_transaction_form(transaction)


def get_transaction(transaction_id):
    """
    Fetch a transaction by ID, ensuring it belongs to the current user's family.
    """
    return Transaction.query.filter(
        Transaction.id == transaction_id,
        Transaction.user_id.in_(get_family_user_ids())
    ).first_or_404()


def handle_transaction_update(transaction):
    """
    Handle the POST request to update a transaction.
    """
    old_amount = transaction.amount
    try:
        update_transaction_fields(transaction)
        db.session.commit()
        current_app.logger.info(
            "Updated transaction ID %d: old amount=%s, new amount=%s",
            transaction.id, old_amount, transaction.amount
        )
        flash("Transaction updated successfully.", "success")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Error updating transaction ID %d: %s", transaction.id, str(e))
        flash("An error occurred while updating the transaction.", "danger")
    return redirect(url_for("transactions.transactions"))


def update_transaction_fields(transaction):
    """
    Update the fields of a transaction based on the form data.
    """
    transaction.amount = request.form.get("amount", transaction.amount)
    transaction.description = request.form.get("description", transaction.description)

    selected_category = request.form.get("category_id", transaction.category_id)
    if selected_category == "other":
        handle_new_category(transaction)
    else:
        transaction.category_id = int(selected_category) if selected_category else None

    transaction.account_id = request.form.get("account_id", type=int)
    transaction.is_transfer = request.form.get("is_transfer") == "on"


def handle_new_category(transaction):
    """
    Handle the creation of a new category if 'other' is selected.
    """
    new_category_name = request.form.get("new_category_name")
    if new_category_name:
        try:
            new_category = Category(name=new_category_name)
            db.session.add(new_category)
            db.session.commit()  # Commit to generate new_category.id
            transaction.category_id = new_category.id
        except Exception as e:
            db.session.rollback()
            current_app.logger.error("Error creating new category: %s", str(e))
            flash("An error occurred while creating the new category.", "danger")
            raise
    else:
        flash("Please enter a new category name.", "danger")
        raise ValueError("New category name is required.")


def render_edit_transaction_form(transaction):
    """
    Render the edit transaction form for a GET request.
    """
    try:
        categories = Category.query.filter_by(family_id=current_user.family_id).all()
        account_types = AccountType.query.filter_by(family_id=current_user.family_id).all()
    except Exception as e:
        current_app.logger.error("Error fetching categories or account types: %s", str(e))
        flash("An error occurred while loading the form.", "danger")
        return redirect(url_for("transactions.transactions"))

    current_app.logger.debug("Rendering edit transaction form for transaction ID %d", transaction.id)
    return render_template(
        "transactions/edit_transaction.html",
        transaction=transaction,
        categories=categories,
        account_types=account_types
    )
