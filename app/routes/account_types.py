from flask import render_template, redirect, url_for, flash, Blueprint, current_app
from flask_login import current_user, login_required
from app import db
from app.models.account_type import AccountType
from app.models.pre_defined_account import PreDefinedAccount
from app.forms.account_type_form import AccountTypeForm


# Blueprint for account types
account_types_bp = Blueprint('account_types', __name__, template_folder='../templates/account_types')


@account_types_bp.route('/account_types')
@login_required
def index():
    """
    List all account types for the current user's family.
    """
    try:
        account_types = AccountType.query.filter_by(family_id=current_user.family_id).all()
        current_app.logger.info("Listing %d account types for family_id %s", len(account_types), current_user.family_id)
    except Exception as e:
        current_app.logger.error("Error fetching account types: %s", str(e))
        flash('An error occurred while fetching account types.', 'danger')
        account_types = []
    return render_template('account_types/index.html', account_types=account_types)


@account_types_bp.route('/account_types/add', methods=['GET', 'POST'])
@login_required
def add_account_type():
    """
    Add a new account type for the current user's family.
    """
    form = AccountTypeForm()
    pre_defined_accounts = fetch_pre_defined_accounts()
    if form.validate_on_submit():
        if create_account_type(form):
            flash('Account type added successfully.', 'success')
            return redirect(url_for('account_types.index'))
    return render_template('account_types/add_account_type.html', form=form, pre_defined_accounts=pre_defined_accounts)


def fetch_pre_defined_accounts():
    """
    Fetch all pre-defined account types from the database.
    """
    try:
        return PreDefinedAccount.query.all()
    except Exception as e:
        current_app.logger.error("Error fetching pre-defined accounts: %s", str(e))
        flash('An error occurred while fetching pre-defined accounts.', 'danger')
        return []


def create_account_type(form):
    """
    Create a new account type in the database.
    """
    try:
        account_type = AccountType(
            name=form.name.data,
            category_field=form.category_field.data,
            date_field=form.date_field.data,
            amount_field=form.amount_field.data,
            description_field=form.description_field.data,
            positive_expense=form.positive_expense.data,
            family_id=current_user.family_id
        )
        db.session.add(account_type)
        db.session.commit()
        current_app.logger.info("Added new account type: %s for family_id %s", account_type.name, current_user.family_id)
        return True
    except Exception as e:
        current_app.logger.error("Error adding account type: %s", str(e))
        flash('An error occurred while adding the account type.', 'danger')
        db.session.rollback()
        return False


@account_types_bp.route('/account_types/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_account_type(id):
    """
    Edit an existing account type for the current user's family.
    """
    account_type = fetch_account_type(id)
    if not account_type:
        return redirect(url_for('account_types.index'))
    form = AccountTypeForm(obj=account_type)
    if form.validate_on_submit():
        if update_account_type(account_type, form):
            flash('Account type updated successfully.', 'success')
            return redirect(url_for('account_types.index'))
    return render_template('account_types/edit_account_type.html', form=form, account_type=account_type)


def fetch_account_type(id):
    """
    Fetch an account type by ID for the current user's family.
    """
    try:
        return AccountType.query.filter_by(id=id, family_id=current_user.family_id).first_or_404()
    except Exception as e:
        current_app.logger.error("Error fetching account type with ID %d: %s", id, str(e))
        flash('An error occurred while fetching the account type.', 'danger')
        return None


def update_account_type(account_type, form):
    """
    Update an existing account type in the database.
    """
    try:
        account_type.name = form.name.data
        account_type.category_field = form.category_field.data
        account_type.date_field = form.date_field.data
        account_type.amount_field = form.amount_field.data
        account_type.description_field = form.description_field.data
        db.session.commit()
        current_app.logger.info("Updated account type: %s (ID: %d) for family_id %s", account_type.name, account_type.id, current_user.family_id)
        return True
    except Exception as e:
        current_app.logger.error("Error updating account type: %s", str(e))
        flash('An error occurred while updating the account type.', 'danger')
        db.session.rollback()
        return False


@account_types_bp.route('/account_types/delete/<int:id>', methods=['POST'])
@login_required
def delete_account_type(id):
    """
    Delete an account type for the current user's family.
    """
    account_type = fetch_account_type(id)
    if not account_type:
        return redirect(url_for('account_types.index'))
    if delete_account_type_from_db(account_type):
        flash('Account type deleted successfully.', 'success')
    return redirect(url_for('account_types.index'))


def delete_account_type_from_db(account_type):
    """
    Delete an account type from the database.
    """
    try:
        db.session.delete(account_type)
        db.session.commit()
        current_app.logger.info("Deleted account type: %s (ID: %d) for family_id %s", account_type.name, account_type.id, current_user.family_id)
        return True
    except Exception as e:
        current_app.logger.error("Error deleting account type: %s", str(e))
        flash('An error occurred while deleting the account type.', 'danger')
        db.session.rollback()
        return False
