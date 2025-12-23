from flask import render_template, redirect, url_for, flash, Blueprint, current_app
from flask_login import current_user, login_required
from app import db
from app.models.account import Account
from app.models.pre_defined_account import PreDefinedAccount
from app.models.user import User
from app.forms.account_type_form import AccountTypeForm
from app.services.reports.net_worth import get_account_balance


# Blueprint for account types (keeping URL structure for backward compatibility)
account_types_bp = Blueprint('account_types', __name__, template_folder='../templates/account_types')


@account_types_bp.route('/account_types')
@login_required
def index():
    """
    List all account types for the current user's family with current balances.
    """
    try:
        account_types = Account.query.filter_by(family_id=current_user.family_id).all()
        current_app.logger.info("Listing %d accounts for family_id %s", len(account_types), current_user.family_id)

        # Get user IDs for balance calculation
        user_ids = [u.id for u in User.query.filter_by(family_id=current_user.family_id).all()]

        # Calculate balance for each account
        account_balances = {}
        for account in account_types:
            account_balances[account.id] = get_account_balance(account, user_ids)

    except Exception as e:
        current_app.logger.error("Error fetching accounts: %s", str(e))
        flash('An error occurred while fetching accounts.', 'danger')
        account_types = []
        account_balances = {}
    return render_template('account_types/index.html', account_types=account_types, account_balances=account_balances)


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
    Create a new account in the database.
    """
    try:
        account = Account(
            name=form.name.data,
            category_field=form.category_field.data,
            date_field=form.date_field.data,
            amount_field=form.amount_field.data,
            description_field=form.description_field.data,
            positive_expense=form.positive_expense.data,
            account_type=form.account_type.data,
            retirement_type=form.retirement_type.data if form.account_type.data == 'retirement' else None,
            initial_balance=form.initial_balance.data or 0,
            family_id=current_user.family_id
        )
        db.session.add(account)
        db.session.commit()
        current_app.logger.info("Added new account: %s for family_id %s", account.name, current_user.family_id)
        return True
    except Exception as e:
        current_app.logger.error("Error adding account: %s", str(e))
        flash('An error occurred while adding the account.', 'danger')
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
    Fetch an account by ID for the current user's family.
    """
    try:
        return Account.query.filter_by(id=id, family_id=current_user.family_id).first_or_404()
    except Exception as e:
        current_app.logger.error("Error fetching account with ID %d: %s", id, str(e))
        flash('An error occurred while fetching the account.', 'danger')
        return None


def update_account_type(account_type, form):
    """
    Update an existing account in the database.
    """
    try:
        account_type.name = form.name.data
        account_type.category_field = form.category_field.data
        account_type.date_field = form.date_field.data
        account_type.amount_field = form.amount_field.data
        account_type.description_field = form.description_field.data
        account_type.positive_expense = form.positive_expense.data
        account_type.account_type = form.account_type.data
        account_type.retirement_type = form.retirement_type.data if form.account_type.data == 'retirement' else None
        account_type.initial_balance = form.initial_balance.data or 0
        db.session.commit()
        current_app.logger.info("Updated account: %s (ID: %d) for family_id %s", account_type.name, account_type.id, current_user.family_id)
        return True
    except Exception as e:
        current_app.logger.error("Error updating account: %s", str(e))
        flash('An error occurred while updating the account.', 'danger')
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
    Delete an account from the database.
    """
    try:
        db.session.delete(account_type)
        db.session.commit()
        current_app.logger.info("Deleted account: %s (ID: %d) for family_id %s", account_type.name, account_type.id, current_user.family_id)
        return True
    except Exception as e:
        current_app.logger.error("Error deleting account: %s", str(e))
        flash('An error occurred while deleting the account.', 'danger')
        db.session.rollback()
        return False
