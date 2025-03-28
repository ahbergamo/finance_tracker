from flask import current_app, flash
from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from app.models.user import User
from app.models.category import Category
from app import db


def get_family_user_ids():
    """
    Retrieve IDs of all users in the current user's family.
    """
    current_app.logger.debug("Getting family user IDs for current_user id=%s, family_id=%s", current_user.id, getattr(current_user, "family_id", None))
    try:
        if current_user.family_id:
            family_users = User.query.filter_by(family_id=current_user.family_id).all()
            ids = [user.id for user in family_users]
            current_app.logger.debug("Found family user IDs: %s", ids)
            return ids
        current_app.logger.debug("No family_id found for current_user, returning own id: %s", current_user.id)
        return [current_user.id]
    except SQLAlchemyError as e:
        current_app.logger.error("Error fetching family user IDs: %s", e)
        return [current_user.id]


def create_or_get_category(category_name):
    """
    Retrieve or create a category for the current user's family.
    """
    current_app.logger.debug("Creating or getting category '%s' for family_id=%s", category_name, getattr(current_user, "family_id", None))
    try:
        category_obj = Category.query.filter_by(name=category_name, family_id=current_user.family_id).first()
        if not category_obj:
            current_app.logger.debug("Category '%s' not found; creating new category.", category_name)
            category_obj = Category(name=category_name, family_id=current_user.family_id)
            db.session.add(category_obj)
            db.session.commit()
            current_app.logger.info("Created new category '%s' for family_id=%s", category_name, current_user.family_id)
        else:
            current_app.logger.debug("Found existing category '%s'", category_name)
        return category_obj
    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Error creating or retrieving category '%s': %s", category_name, e)
        flash(f"An error occurred while processing the category '{category_name}'. Please try again.", "danger")
        return None


def apply_date_filter(query, date_str, date_type):
    """
    Apply a date filter to the query based on a date string.
    """
    current_app.logger.debug("Applying %s date filter with date string: %s", date_type, date_str)
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        from app.models.transaction import Transaction
        if date_type == "start":
            query = query.filter(Transaction.timestamp >= date_obj)
            current_app.logger.debug("Applied start date filter: %s", date_obj)
        elif date_type == "end":
            query = query.filter(Transaction.timestamp <= date_obj)
            current_app.logger.debug("Applied end date filter: %s", date_obj)
    except ValueError:
        current_app.logger.error("Invalid %s date format: %s", date_type, date_str)
        flash(f"Invalid {date_type} date format.", "danger")
    return query
