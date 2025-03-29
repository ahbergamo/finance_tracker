from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import current_user, login_required
from app.models.category import Category
from app.services.category import (
    get_categories_for_user,
    add_category,
    update_category,
    delete_category_from_db
)
from app.models.transaction import Transaction
from flask import abort
from app import db


categories_bp = Blueprint("categories", __name__)


@categories_bp.route("/categories", methods=["GET", "POST"])
@login_required
def manage_categories():
    """
    Handle category management: display categories and add new ones.
    """
    if request.method == "POST":
        name = request.form.get("name")
        if not name:
            flash("Category name cannot be empty.", "danger")
            current_app.logger.warning("Attempted to add an empty category name.")
        elif Category.query.filter_by(name=name).first():
            flash("Category already exists.", "warning")
            current_app.logger.info("Attempted to add duplicate category: %s", name)
        else:
            add_category(name, current_user.family_id)
        return redirect(url_for("categories.manage_categories"))

    categories = get_categories_for_user(current_user.family_id)
    return render_template("categories/index.html", categories=categories)


@categories_bp.route("/categories/edit/<int:category_id>", methods=["GET", "POST"])
@login_required
def edit_category(category_id):
    """
    Handle editing an existing category.
    """
    category = db.session.get(Category, category_id)
    if category is None:
        abort(404)
    if request.method == "POST":
        name = request.form.get("name")
        if not name:
            flash("Category name cannot be empty.", "danger")
            current_app.logger.warning("Empty category name submitted for category ID %d", category_id)
        else:
            update_category(category, name)
        return redirect(url_for("categories.manage_categories"))

    return render_template("categories/edit_category.html", category=category)


@categories_bp.route("/categories/delete/<int:category_id>", methods=["POST"])
@login_required
def delete_category(category_id):
    """
    Handle deleting a category, ensuring it is not in use by any transactions.
    """
    category = db.session.get(Category, category_id)
    if category is None:
        abort(404)
    try:
        used_count = Transaction.query.filter_by(category_id=category.id).count()
        if used_count > 0:
            flash(
                f"Category is currently in use by {used_count} transaction(s). "
                "Please delete or reassign those transactions before deleting this category.",
                "danger"
            )
            current_app.logger.warning(
                "Attempted to delete category ID %d that is in use by %d transaction(s)",
                category_id, used_count
            )
            return redirect(url_for("categories.manage_categories"))

        delete_category_from_db(category)
    except Exception as e:
        current_app.logger.error("Error checking or deleting category ID %d: %s", category_id, str(e))
        flash("An error occurred while deleting the category.", "danger")

    return redirect(url_for("categories.manage_categories"))
