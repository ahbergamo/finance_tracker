from flask import current_app, flash
from app import db
from app.models.import_rule import ImportRule
from app.models.account_type import AccountType
from app.models.category import Category
from app.models.user import User


def fetch_account_types_and_categories(family_id):
    """
    Fetch account types and categories for the given family ID.
    """
    current_app.logger.debug("Fetching account types and categories for family_id=%s", family_id)
    try:
        account_types = AccountType.query.filter_by(family_id=family_id).all()
        categories = Category.query.filter_by(family_id=family_id).all()
        current_app.logger.debug("Fetched %d account types and %d categories for family_id=%s",
                                 len(account_types), len(categories), family_id)
        return account_types, categories
    except Exception as e:
        current_app.logger.error("Error fetching account types or categories for family_id=%s: %s", family_id, str(e))
        flash("An error occurred while fetching account types or categories.", "danger")
        return [], []


def process_override_category(form_data, family_id):
    """
    Process the override category field from the form data.
    Returns the override_category_id as an integer if set, or None if not valid.
    """
    current_app.logger.debug("Processing override category for family_id=%s with form_data=%s", family_id, form_data)
    override_category_value = form_data.get("override_category", "").strip() or None
    if override_category_value == "other":
        new_category_name = form_data.get("new_category_name")
        if new_category_name:
            current_app.logger.debug("Override value is 'other'; creating or retrieving new category: %s", new_category_name)
            category = get_or_create_category(new_category_name.strip(), family_id)
            if category:
                current_app.logger.info("Override category created with ID %s", category.id)
                return category.id
            else:
                current_app.logger.error("Failed to create new category for override with name: %s", new_category_name)
                return None
        else:
            flash("Please enter a new category name for override.", "danger")
            current_app.logger.warning("Override category selected as 'other' but no new category name provided.")
            return None
    elif override_category_value:
        try:
            override_id = int(override_category_value)
            current_app.logger.debug("Override category provided as ID: %s", override_id)
            return override_id
        except ValueError:
            current_app.logger.error("Invalid override category value: %s", override_category_value)
            return None
    current_app.logger.debug("No override category provided.")
    return None


def get_or_create_category(category_name, family_id):
    """
    Retrieve or create a category by name for the given family.
    """
    current_app.logger.debug("Getting or creating category '%s' for family_id=%s", category_name, family_id)
    category = Category.query.filter_by(name=category_name, family_id=family_id).first()
    if not category:
        current_app.logger.debug("Category '%s' not found. Creating new category.", category_name)
        category = Category(name=category_name, family_id=family_id)
        db.session.add(category)
        try:
            db.session.commit()  # Commit to generate the category ID
            current_app.logger.info("Created new category '%s' with ID %s for family_id=%s", category_name, category.id, family_id)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error("Error creating category '%s' for family_id=%s: %s", category_name, family_id, e)
            return None
    else:
        current_app.logger.debug("Found existing category '%s' with ID %s", category_name, category.id)
    return category


def create_import_rule(family_id, account_type_value, field_to_match, match_pattern, is_transfer, override_category_id):
    """
    Create a new ImportRule record.
    """
    current_app.logger.debug("Creating import rule for family_id=%s", family_id)
    rule = ImportRule(
        account_type=account_type_value,
        field_to_match=field_to_match.strip(),
        match_pattern=match_pattern.strip(),
        is_transfer=is_transfer,
        override_category_id=override_category_id,
        family_id=family_id
    )
    try:
        db.session.add(rule)
        db.session.commit()
        current_app.logger.info("Added new import rule: %s for family_id=%s", rule, family_id)
        flash('Import rule added successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Error adding import rule for family_id=%s: %s", family_id, str(e))
        flash("An error occurred while adding the import rule.", "danger")


def update_import_rule(rule, account_type_value, field_to_match, match_pattern, is_transfer, override_category_id):
    """
    Update an existing ImportRule record.
    """
    current_app.logger.debug("Updating import rule ID %s", rule.id)
    rule.account_type = account_type_value
    rule.field_to_match = field_to_match.strip()
    rule.match_pattern = match_pattern.strip()
    rule.is_transfer = is_transfer
    rule.override_category_id = override_category_id
    try:
        db.session.commit()
        current_app.logger.info("Updated import rule ID %d: %s (family_id=%s)", rule.id, rule, rule.family_id)
        flash('Import rule updated successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Error updating import rule ID %d: %s", rule.id, str(e))
        flash("An error occurred while updating the import rule.", "danger")


def delete_import_rule(rule):
    """
    Permanently delete an ImportRule record from the database.
    """
    current_app.logger.debug("Deleting import rule ID %s", rule.id)
    try:
        db.session.delete(rule)
        db.session.commit()
        current_app.logger.info("Deleted import rule ID %d: %s (family_id=%s)", rule.id, rule, rule.family_id)
        flash('Import rule deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Error deleting import rule ID %s: %s", rule.id, str(e))
        flash("An error occurred while deleting the import rule.", "danger")


def apply_rule_to_transactions(rule, family_user_ids):
    """
    Apply the given rule to all relevant transactions for the provided family user IDs.
    Returns the count of updated transactions.
    """
    from app.models.transaction import Transaction

    current_app.logger.debug("Applying rule ID %s to transactions for family_user_ids=%s", rule.id, family_user_ids)
    try:
        transactions = Transaction.query.filter(Transaction.user_id.in_(family_user_ids)).all()
        current_app.logger.debug("Found %d transactions for rule application", len(transactions))
        count = 0
        for tx in transactions:
            value = get_transaction_field_value(tx, rule.field_to_match)
            if rule.match_pattern in value:
                tx.is_transfer = rule.is_transfer
                if rule.override_category_id:
                    tx.category_id = rule.override_category_id
                count += 1
        db.session.commit()
        current_app.logger.info("Applied rule ID %s to %d transactions", rule.id, count)
        return count
    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Error applying rule ID %s: %s", rule.id, str(e))
        flash("An error occurred while applying the rule.", "danger")
        return 0


def get_transaction_field_value(transaction, field_to_match):
    """
    Get the value of the specified field from a transaction.
    """
    if field_to_match.lower() == "description":
        return transaction.description or ""
    elif field_to_match.lower() == "category":
        return transaction.category.name if transaction.category else ""
    return ""


def get_family_user_ids(family_id):
    """
    Retrieve IDs of all users in the given family.
    """
    current_app.logger.debug("Retrieving family user IDs for family_id=%s", family_id)
    try:
        users = User.query.filter_by(family_id=family_id).all()
        ids = [u.id for u in users]
        current_app.logger.debug("Found %d users for family_id=%s", len(ids), family_id)
        return ids
    except Exception as e:
        current_app.logger.error("Error retrieving family user IDs for family_id=%s: %s", family_id, str(e))
        return []
