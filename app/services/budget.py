from datetime import datetime
from flask import current_app
from app import db
from app.models.budget import Budget
from app.models.category import Category


def add_budget(user_id, name, category_ids, amount, start_date, end_date):
    """
    Adds a new budget entry to the database.

    Args:
        user_id (int): The ID of the user creating the budget.
        name (str): The name of the budget.
        category_ids (list of int): List of category IDs associated with the budget.
        amount (float or str): The budget amount.
        start_date (str): The start date in 'YYYY-MM-DD' format.
        end_date (str): The end date in 'YYYY-MM-DD' format.

    Returns:
        bool: True if the budget was successfully added, False otherwise.
    """
    current_app.logger.debug("Adding budget for user_id=%s, name='%s', amount=%s", user_id, name, amount)
    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None

        # Retrieve selected categories from the list of IDs
        selected_categories = (
            Category.query.filter(Category.id.in_(category_ids)).all()
            if category_ids else []
        )
        current_app.logger.debug("Selected categories for budget: %s", selected_categories)

        budget = Budget(
            user_id=user_id,
            name=name,
            amount=float(amount),
            start_date=start_date_obj,
            end_date=end_date_obj,
            categories=selected_categories
        )
        db.session.add(budget)
        db.session.commit()
        current_app.logger.info("Budget '%s' added successfully for user_id=%s", name, user_id)
        return True
    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Error adding budget '%s' for user_id=%s: %s", name, user_id, e)
        return False


def edit_budget(budget, name, category_ids, amount, start_date, end_date):
    """
    Updates an existing budget.

    Args:
        budget (Budget): The budget object to update.
        name (str): New budget name.
        category_ids (list of int): List of new category IDs.
        amount (float or str): New amount.
        start_date (str): New start date (YYYY-MM-DD) or None.
        end_date (str): New end date (YYYY-MM-DD) or None.

    Returns:
        bool: True if the update succeeded, False otherwise.
    """
    current_app.logger.debug("Editing budget id=%s", budget.id)
    try:
        budget.name = name
        budget.amount = float(amount)
        budget.start_date = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
        budget.end_date = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None

        # Update categories relationship
        selected_categories = (
            Category.query.filter(Category.id.in_(category_ids)).all()
            if category_ids else []
        )
        current_app.logger.debug("New selected categories for budget id=%s: %s", budget.id, selected_categories)
        budget.categories = selected_categories

        db.session.add(budget)  # Ensure the budget object is marked for update
        db.session.commit()
        current_app.logger.info("Budget id=%s updated successfully", budget.id)
        return True
    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Error updating budget id=%s: %s", budget.id, e)
        return False


def delete_budget(budget):
    """
    Deletes the given budget from the database.

    Args:
        budget (Budget): The budget to delete.

    Returns:
        bool: True if deletion succeeded, False otherwise.
    """
    current_app.logger.debug("Deleting budget id=%s", budget.id)
    try:
        db.session.delete(budget)
        db.session.commit()
        current_app.logger.info("Budget id=%s deleted successfully", budget.id)
        return True
    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Error deleting budget id=%s: %s", budget.id, e)
        return False
