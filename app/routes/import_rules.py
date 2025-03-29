from flask import Blueprint, render_template, redirect, url_for, flash, current_app, request
from flask_login import current_user, login_required
from app.models.import_rule import ImportRule
from app.forms.import_rule_form import ImportRuleForm
from app.services.import_rules import (
    fetch_account_types_and_categories,
    process_override_category,
    get_family_user_ids,
    create_import_rule,
    update_import_rule,
    delete_import_rule,
    apply_rule_to_transactions,
)


import_rules_bp = Blueprint('import_rules', __name__, template_folder='../templates/import_rules')


@import_rules_bp.route('/import_rules')
@login_required
def index():
    """
    Display all import rules for the current user's family.
    """
    try:
        rules = ImportRule.query.filter_by(family_id=current_user.family_id).all()
        current_app.logger.info("Retrieved %d import rules for family_id %s", len(rules), current_user.family_id)
    except Exception as e:
        current_app.logger.error("Error retrieving import rules: %s", str(e))
        flash("An error occurred while retrieving import rules.", "danger")
        rules = []
    return render_template('import_rules/index.html', rules=rules)


@import_rules_bp.route('/import_rules/add', methods=['GET', 'POST'])
@login_required
def add_rule():
    form = ImportRuleForm(current_user.family_id)
    account_types, categories = fetch_account_types_and_categories(current_user.family_id)

    if form.validate_on_submit():
        account_type_value = request.form.get("account_type", "").strip() or None
        override_category_id = process_override_category(request.form, current_user.family_id)
        if override_category_id is None:
            return redirect(url_for("import_rules.add_rule"))

        create_import_rule(
            family_id=current_user.family_id,
            account_type_value=account_type_value,
            field_to_match=form.field_to_match.data,
            match_pattern=form.match_pattern.data,
            is_transfer=form.is_transfer.data,
            override_category_id=override_category_id
        )
        return redirect(url_for('import_rules.index'))

    current_app.logger.debug("Form errors: %s", form.errors)
    return render_template('import_rules/add_rule.html', form=form, account_types=account_types, categories=categories)


@import_rules_bp.route('/import_rules/edit/<int:rule_id>', methods=['GET', 'POST'])
@login_required
def edit_rule(rule_id):
    rule = ImportRule.query.filter_by(id=rule_id, family_id=current_user.family_id).first_or_404()
    form = ImportRuleForm(current_user.family_id, obj=rule)
    account_types, categories = fetch_account_types_and_categories(current_user.family_id)

    if rule.override_category_id:
        form.override_category.data = str(rule.override_category_id)

    if form.validate_on_submit():
        account_type_value = request.form.get("account_type", "").strip() or None
        override_category_id = process_override_category(request.form, current_user.family_id)
        if override_category_id is None:
            return redirect(url_for("import_rules.edit_rule", rule_id=rule_id))

        update_import_rule(
            rule=rule,
            account_type_value=account_type_value,
            field_to_match=form.field_to_match.data,
            match_pattern=form.match_pattern.data,
            is_transfer=form.is_transfer.data,
            override_category_id=override_category_id
        )
        return redirect(url_for('import_rules.index'))

    current_app.logger.debug("Rendering edit form for import rule ID %d", rule_id)
    return render_template('import_rules/edit_rule.html', form=form, rule=rule, account_types=account_types, categories=categories)


@import_rules_bp.route('/import_rules/delete/<int:rule_id>', methods=['POST'])
@login_required
def delete_rule(rule_id):
    rule = ImportRule.query.filter_by(id=rule_id, family_id=current_user.family_id).first_or_404()
    delete_import_rule(rule)
    return redirect(url_for('import_rules.index'))


@import_rules_bp.route('/import_rules/apply/<int:rule_id>', methods=['POST'])
@login_required
def apply_rule(rule_id):
    rule = ImportRule.query.filter_by(id=rule_id, family_id=current_user.family_id).first_or_404()
    family_user_ids = get_family_user_ids(current_user.family_id)
    count = apply_rule_to_transactions(rule, family_user_ids)
    flash(f"Rule applied to {count} transactions.", "success")
    current_app.logger.info("Applied rule ID %d to %d transactions for family_id %s", rule_id, count, current_user.family_id)
    return redirect(url_for('import_rules.index'))
