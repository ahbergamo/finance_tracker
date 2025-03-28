from flask import Blueprint, current_app, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import func
from app.models.budget import Budget
from app.models.category import Category
from app.models.transaction import Transaction
from app import db
from app.models.user import User
from app.forms.budget_form import EditBudgetForm, AddBudgetForm


budgets_bp = Blueprint("budgets", __name__)


def get_selected_categories(category_ids):
    """Retrieve categories by their IDs."""
    try:
        return Category.query.filter(Category.id.in_(category_ids)).all() if category_ids else []
    except Exception as e:
        current_app.logger.error(e)
        flash("Error retrieving categories.", "danger")
        return []


def get_family_user_ids():
    """Retrieve IDs of the current user and their family members."""
    family_user_ids = [current_user.id]
    if current_user.family_id:
        try:
            family_users = User.query.filter_by(family_id=current_user.family_id).all()
            family_user_ids = [user.id for user in family_users]
        except Exception as e:
            current_app.logger.error(e)
            flash("Error retrieving family members.", "danger")
    return family_user_ids


def calculate_total_spent_per_category(family_user_ids, category_ids):
    """Calculate total spent per category for the given user IDs."""
    try:
        return {
            category_id: db.session.query(func.sum(Transaction.amount))
            .filter(
                Transaction.user_id.in_(family_user_ids),
                Transaction.category_id == category_id
            ).scalar() or 0
            for category_id in category_ids
        }
    except Exception as e:
        current_app.logger.error(e)
        flash("Error calculating total spent per category.", "danger")
        return {}


def calculate_budget_details(user_budgets, family_user_ids):
    """Calculate detailed budget information."""
    detailed_budgets = []
    for budget in user_budgets:
        try:
            category_ids = [category.id for category in budget.categories]
            total_spent = db.session.query(func.sum(Transaction.amount)).filter(
                Transaction.user_id.in_(family_user_ids),
                Transaction.category_id.in_(category_ids),
                Transaction.timestamp >= budget.start_date,
                Transaction.timestamp <= budget.end_date
            ).scalar() or 0

            remaining = budget.amount - abs(total_spent)

            detailed_budgets.append({
                "id": budget.id,
                "name": budget.name,
                "amount": budget.amount,
                "spent": total_spent,
                "remaining": remaining,
                "start_date": budget.start_date.strftime("%Y-%m-%d") if budget.start_date else "N/A",
                "end_date": budget.end_date.strftime("%Y-%m-%d") if budget.end_date else "N/A",
                "categories": [category.name for category in budget.categories]
            })
        except Exception as e:
            current_app.logger.error(e)
            flash(f"Error calculating details for budget {budget.name}.", "danger")
    return detailed_budgets


# --- Route for viewing budgets and handling budget creation via POST to /budgets ---
@budgets_bp.route("/budgets", methods=["GET", "POST"])
@login_required
def budgets():
    from app.services.budget import add_budget  # import service function
    if request.method == "POST":
        name = request.form.get("name")
        amount = request.form.get("amount")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        # Convert the incoming category_ids (strings) to integers
        try:
            category_ids = [int(cid) for cid in request.form.getlist("category_ids") if cid]
        except ValueError:
            category_ids = []
        if add_budget(user_id=current_user.id, name=name, category_ids=category_ids,
                      amount=amount, start_date=start_date, end_date=end_date):
            flash("Budget added successfully.", "success")
        else:
            flash("Failed to add budget.", "danger")
        return redirect(url_for("budgets.budgets"))

    family_user_ids = get_family_user_ids()
    try:
        categories = Category.query.filter_by(family_id=current_user.family_id).all()
        categories_dict = {category.id: category.name for category in categories}
        user_budgets = Budget.query.filter(Budget.user_id.in_(family_user_ids)).options(db.joinedload(Budget.categories)).all()
        category_ids = {c.id for budget in user_budgets for c in budget.categories}
        detailed_budgets = calculate_budget_details(user_budgets, family_user_ids)
    except Exception as e:
        current_app.logger.error(e)
        flash("Error retrieving budgets or categories.", "danger")
        return render_template("budgets/index.html", budgets=[], categories={})

    return render_template("budgets/index.html", budgets=detailed_budgets, categories=categories_dict)


# --- Route for deleting a budget ---
@budgets_bp.route("/budgets/delete/<int:budget_id>", methods=["POST"])
@login_required
def delete_budget(budget_id):
    from app.services.budget import delete_budget as service_delete_budget
    try:
        budget = Budget.query.filter_by(id=budget_id, user_id=current_user.id).first_or_404()
        if service_delete_budget(budget):
            flash("Budget deleted successfully.", "success")
        else:
            flash("Failed to delete budget.", "danger")
    except Exception as e:
        current_app.logger.error(e)
        flash("Error deleting budget.", "danger")
    return redirect(url_for("budgets.budgets"))


@budgets_bp.route("/budgets/edit/<int:budget_id>", methods=["GET", "POST"])
@login_required
def edit_budget(budget_id):
    from app.services.budget import edit_budget as service_edit_budget
    try:
        budget = Budget.query.filter_by(id=budget_id, user_id=current_user.id).first_or_404()
        form = EditBudgetForm(current_user.family_id, obj=budget)

        # Populate category choices
        categories = Category.query.filter_by(family_id=current_user.family_id).all()
        form.category_ids.choices = [(c.id, c.name) for c in categories]

        # Only pre-populate the category_ids field on GET requests.
        if request.method == "GET":
            form.category_ids.data = [c.id for c in budget.categories] if budget.categories else []

        if form.validate_on_submit():
            # On POST, WTForms will process the submitted data into form.category_ids.data.
            category_ids = form.category_ids.data if form.category_ids.data else []
            # (Optional) log the submitted category IDs for debugging:
            current_app.logger.debug("Submitted category_ids: %s", category_ids)

            success = service_edit_budget(
                budget,
                name=form.name.data,
                category_ids=category_ids,
                amount=form.amount.data,
                start_date=form.start_date.data.strftime("%Y-%m-%d") if form.start_date.data else None,
                end_date=form.end_date.data.strftime("%Y-%m-%d") if form.end_date.data else None
            )
            if success:
                flash("Budget updated successfully.", "success")
            else:
                flash("Failed to update budget.", "danger")
            return redirect(url_for("budgets.budgets"))
    except Exception as e:
        current_app.logger.error(e)
        flash("Error editing budget.", "danger")

    return render_template("budgets/edit_budget.html", form=form)


# --- Dedicated route for a separate 'add budget' page ---
@budgets_bp.route("/budgets/add", methods=["GET", "POST"])
@login_required
def add_budget_page():
    form = AddBudgetForm(current_user.family_id)
    try:
        categories = Category.query.filter_by(family_id=current_user.family_id).all()
        form.category_ids.choices = sorted([(c.id, c.name) for c in categories], key=lambda x: x[1].lower())
        if form.validate_on_submit():
            try:
                category_ids = form.category_ids.data if form.category_ids.data else []
            except Exception:
                category_ids = []
            from app.services.budget import add_budget
            success = add_budget(
                user_id=current_user.id,
                name=form.name.data,
                category_ids=category_ids,
                amount=form.amount.data,
                start_date=form.start_date.data.strftime("%Y-%m-%d") if form.start_date.data else None,
                end_date=form.end_date.data.strftime("%Y-%m-%d") if form.end_date.data else None
            )
            if success:
                flash("Budget added successfully.", "success")
            else:
                flash("Error adding budget.", "danger")
            return redirect(url_for("budgets.budgets"))
    except Exception as e:
        current_app.logger.error(e)
        flash("Error adding budget.", "danger")
    return render_template("budgets/add_budget.html", form=form)
