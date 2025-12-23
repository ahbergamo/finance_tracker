from flask import render_template, redirect, url_for, flash, Blueprint, current_app
from flask_login import current_user, login_required
from app import db
from app.models.account import Account
from app.models.account_balance_history import AccountBalanceHistory
from app.forms.balance_history_form import BalanceHistoryForm


balance_history_bp = Blueprint('balance_history', __name__, template_folder='../templates/balance_history')

# Account types that use balance history instead of transactions
BALANCE_HISTORY_TYPES = ('retirement', 'brokerage', 'real_estate', 'vehicle', 'other_asset', 'loan')


@balance_history_bp.route('/accounts/<int:account_id>/balances')
@login_required
def index(account_id):
    """
    View balance history for an account.
    """
    account = Account.query.filter_by(
        id=account_id,
        family_id=current_user.family_id
    ).first_or_404()

    # Only balance-history type accounts have balance history
    if account.account_type not in BALANCE_HISTORY_TYPES:
        flash('Balance history is only available for asset/liability accounts.', 'warning')
        return redirect(url_for('account_types.index'))

    balances = AccountBalanceHistory.query.filter_by(
        account_id=account_id
    ).order_by(AccountBalanceHistory.as_of_date.desc()).all()

    form = BalanceHistoryForm()

    return render_template(
        'balance_history/index.html',
        account=account,
        balances=balances,
        form=form
    )


@balance_history_bp.route('/accounts/<int:account_id>/balances/add', methods=['POST'])
@login_required
def add_balance(account_id):
    """
    Add a balance history entry.
    """
    account = Account.query.filter_by(
        id=account_id,
        family_id=current_user.family_id
    ).first_or_404()

    if account.account_type not in BALANCE_HISTORY_TYPES:
        flash('Balance history is only available for asset/liability accounts.', 'warning')
        return redirect(url_for('account_types.index'))

    form = BalanceHistoryForm()
    if form.validate_on_submit():
        # Check for existing entry on same date
        existing = AccountBalanceHistory.query.filter_by(
            account_id=account_id,
            as_of_date=form.as_of_date.data
        ).first()

        if existing:
            # Update existing entry
            existing.balance = form.balance.data
            existing.notes = form.notes.data
            flash('Balance updated for existing date.', 'info')
        else:
            # Create new entry
            balance_entry = AccountBalanceHistory(
                account_id=account_id,
                balance=form.balance.data,
                as_of_date=form.as_of_date.data,
                notes=form.notes.data
            )
            db.session.add(balance_entry)
            flash('Balance added successfully.', 'success')

        db.session.commit()
        current_app.logger.info(
            "Added balance $%s for account %s on %s",
            form.balance.data,
            account.name,
            form.as_of_date.data
        )
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'danger')

    return redirect(url_for('balance_history.index', account_id=account_id))


@balance_history_bp.route('/accounts/<int:account_id>/balances/<int:balance_id>/delete', methods=['POST'])
@login_required
def delete_balance(account_id, balance_id):
    """
    Delete a balance history entry.
    """
    account = Account.query.filter_by(
        id=account_id,
        family_id=current_user.family_id
    ).first_or_404()

    balance = AccountBalanceHistory.query.filter_by(
        id=balance_id,
        account_id=account_id
    ).first_or_404()

    db.session.delete(balance)
    db.session.commit()

    flash('Balance entry deleted.', 'success')
    current_app.logger.info(
        "Deleted balance entry %d for account %s",
        balance_id,
        account.name
    )

    return redirect(url_for('balance_history.index', account_id=account_id))
