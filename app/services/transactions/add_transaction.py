from flask import render_template, redirect, url_for, flash, current_app
from flask_login import current_user
from app import db
from app.models.transaction import Transaction
from app.models.category import Category
from app.models.account_type import AccountType
from app.services.transactions.utilities import create_or_get_category


def process_add_transaction(form):
    """
    Process the POST data to add a new transaction.
    Returns a tuple (new_transaction, error_flag). If an error occurs,
    error_flag can be used to indicate that the caller should redirect.
    """
    current_app.logger.debug("Starting process_add_transaction with form data: %s", form)
    amount = form.get("amount")
    description = form.get("description")
    selected_category = form.get("category_id")
    account_id = form.get("account_id", type=int)
    current_app.logger.debug("Retrieved form values - amount: %s, description: %s, selected_category: %s, account_id: %s",
                             amount, description, selected_category, account_id)

    # Retrieve or create the category
    category_obj = create_or_get_category(selected_category)
    if category_obj is None:
        current_app.logger.error("Failed to create or retrieve category for selected value: %s", selected_category)
        return None, "redirect"

    # (NOTE: original code uses category_obj.name for category_id; adjust if needed)
    category_name = category_obj.name
    current_app.logger.debug("Using category: %s", category_name)

    current_app.logger.info("Adding transaction: amount=%s, category_id=%s, account_id=%s",
                            amount, category_name, account_id)

    try:
        new_transaction = Transaction(
            amount=amount,
            description=description,
            category_id=category_name,  # use category_name as in original code
            user_id=current_user.id,
            account_id=account_id
        )
        db.session.add(new_transaction)
        db.session.commit()
        current_app.logger.info("Transaction added successfully for user %s", current_user.id)
        flash("Transaction added successfully.", "success")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Error adding transaction for user %s: %s", current_user.id, str(e))
        flash("An error occurred while adding the transaction. Please try again.", "danger")

    return new_transaction, None


def render_add_transaction_form():
    """
    Render and return the add transaction form.
    """
    current_app.logger.debug("Rendering add transaction form for user %s", current_user.id)
    try:
        categories = Category.query.filter_by(family_id=current_user.family_id).all()
        account_types = AccountType.query.filter_by(family_id=current_user.family_id).all()
        current_app.logger.debug("Retrieved %d categories and %d account types for family_id %s",
                                 len(categories), len(account_types), current_user.family_id)
    except Exception as e:
        current_app.logger.error("Error fetching categories or account types for user %s: %s", current_user.id, str(e))
        flash("An error occurred while loading the form. Please try again.", "danger")
        return redirect(url_for("transactions.transactions"))

    return render_template("transactions/add_transaction.html", categories=categories, account_types=account_types)
