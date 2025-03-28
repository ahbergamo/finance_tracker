from flask import current_app, flash
from app.models.category import Category
from app import db


def get_categories_for_user(family_id):
    """
    Retrieve all categories for a given family, ordered alphabetically.
    """
    current_app.logger.debug("get_categories_for_user called with family_id=%s", family_id)
    try:
        categories = Category.query.filter_by(family_id=family_id).order_by(Category.name.asc()).all()
        current_app.logger.debug("Retrieved %d categories for family_id=%s", len(categories), family_id)
        return categories
    except Exception as e:
        current_app.logger.error("Error retrieving categories for family_id=%s: %s", family_id, str(e))
        flash("An error occurred while retrieving categories.", "danger")
        return []


def add_category(name, family_id):
    """
    Add a new category to the database.

    Args:
        name (str): The name of the category.
        family_id (int): The family ID to associate the category with.
    """
    current_app.logger.debug("add_category called with name='%s' for family_id=%s", name, family_id)
    try:
        new_category = Category(name=name, family_id=family_id)
        db.session.add(new_category)
        db.session.commit()
        current_app.logger.info("Added new category '%s' for family_id=%s", name, family_id)
        flash("Category added successfully.", "success")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Error adding category '%s' for family_id=%s: %s", name, family_id, str(e))
        flash("An error occurred while adding the category.", "danger")


def update_category(category, name):
    """
    Update an existing category's name.
    """
    current_app.logger.debug("update_category called for category_id=%s with new name='%s'", category.id, name)
    try:
        current_app.logger.info("Updating category ID %d from '%s' to '%s'", category.id, category.name, name)
        category.name = name
        db.session.commit()
        current_app.logger.info("Category ID %d updated successfully", category.id)
        flash("Category updated successfully.", "success")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Error updating category ID %d: %s", category.id, str(e))
        flash("An error occurred while updating the category.", "danger")


def delete_category_from_db(category):
    """
    Delete a category from the database.
    """
    current_app.logger.debug("delete_category_from_db called for category_id=%s", category.id)
    try:
        db.session.delete(category)
        db.session.commit()
        current_app.logger.info("Deleted category ID %d with name '%s'", category.id, category.name)
        flash("Category deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Error deleting category ID %d: %s", category.id, str(e))
        flash("An error occurred while deleting the category.", "danger")
