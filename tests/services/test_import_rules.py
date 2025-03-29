import pytest
from app import db
from app.models.user import User
from app.models.import_rule import ImportRule
from app.models.category import Category
from app.models.account_type import AccountType
from app.services.import_rules import (
    fetch_account_types_and_categories,
    process_override_category,
    create_import_rule,
    update_import_rule,
    delete_import_rule,
    apply_rule_to_transactions,
    get_family_user_ids,
    get_transaction_field_value
)


@pytest.fixture
def family_user(app):
    """
    Return a seeded user from the 'Family_1' family. For example, 'user1'.
    This ensures we have user.family_id to test with.
    """
    with app.app_context():
        user = User.query.filter_by(username="user1").first()
        assert user is not None, "Seed data must contain user 'user1'."
        yield user


@pytest.fixture
def request_context(app):
    """
    Provide a Flask request context so flash() and others won't fail.
    """
    with app.test_request_context():
        yield


@pytest.fixture(autouse=True)
def clear_import_rules(app):
    """
    Clear the ImportRule table before each test, so leftover data
    doesn't cause test interference.
    """
    with app.app_context():
        db.session.query(ImportRule).delete()
        db.session.commit()
    yield


def test_fetch_account_types_and_categories(app, family_user, request_context):
    with app.app_context():
        acct_types, cats = fetch_account_types_and_categories(family_user.family_id)
        # Just confirm they're lists (they may be empty or populated based on seed).
        assert isinstance(acct_types, list)
        assert isinstance(cats, list)


def test_process_override_category_other(app, family_user, request_context):
    with app.app_context():
        form_data = {
            "override_category": "other",
            "new_category_name": "BrandNewCat"
        }
        cat_id = process_override_category(form_data, family_user.family_id)
        assert cat_id is not None
        cat = db.session.get(Category, cat_id)
        assert cat is not None
        assert cat.name == "BrandNewCat"
        assert cat.family_id == family_user.family_id


def test_create_import_rule(app, family_user, request_context):
    with app.app_context():
        create_import_rule(
            family_id=family_user.family_id,
            account_type_value="Chase Checking",
            field_to_match="Description",
            match_pattern="TEST",
            is_transfer=True,
            override_category_id=None
        )
        count = ImportRule.query.count()
        assert count == 1


def test_update_import_rule(app, family_user, request_context):
    with app.app_context():
        rule = ImportRule(
            account_type="Chase Checking",
            field_to_match="Description",
            match_pattern="OLD_PATTERN",
            is_transfer=False,
            family_id=family_user.family_id
        )
        db.session.add(rule)
        db.session.commit()
        rule_id = rule.id

        update_import_rule(
            rule=rule,
            account_type_value="Chase Savings",
            field_to_match="Category",
            match_pattern="NEW_PATTERN",
            is_transfer=True,
            override_category_id=None
        )
        updated = db.session.get(ImportRule, rule_id)
        assert updated.account_type == "Chase Savings"
        assert updated.field_to_match == "Category"
        assert updated.match_pattern == "NEW_PATTERN"
        assert updated.is_transfer is True


def test_delete_import_rule(app, family_user, request_context):
    with app.app_context():
        rule = ImportRule(
            account_type="Chase Checking",
            field_to_match="Description",
            match_pattern="TO_DELETE",
            is_transfer=False,
            family_id=family_user.family_id
        )
        db.session.add(rule)
        db.session.commit()
        rule_id = rule.id

        delete_import_rule(rule)
        gone = db.session.get(ImportRule, rule_id)
        assert gone is None


def test_apply_rule_to_transactions(app, family_user, request_context):
    """
    Test applying a rule to relevant transactions. Provide non-null
    category_id, amount, account_id referencing a real AccountType row.
    """
    from app.models.transaction import Transaction

    with app.app_context():
        # 1) Find a seeded AccountType row for the same family (e.g., "Chase Checking").
        seeded_acct_type = AccountType.query.filter_by(name="Chase Checking", family_id=family_user.family_id).first()
        assert seeded_acct_type, "No seeded 'Chase Checking' AccountType found for user's family."

        # 2) Create a new category
        cat = Category(name="TempCat", family_id=family_user.family_id)
        db.session.add(cat)
        db.session.commit()

        # 3) Create an ImportRule
        rule = ImportRule(
            account_type="Chase Checking",
            field_to_match="Description",
            match_pattern="MATCHME",
            is_transfer=False,
            family_id=family_user.family_id
        )
        db.session.add(rule)
        db.session.commit()

        # 4) Insert a matching transaction
        tx = Transaction(
            user_id=family_user.id,
            description="PLEASE MATCHME",
            amount=100.0,
            category_id=cat.id,
            account_id=seeded_acct_type.id,  # references the account_types table
            is_transfer=False
        )
        db.session.add(tx)
        db.session.commit()

        # 5) Apply the rule
        fam_ids = get_family_user_ids(family_user.family_id)
        count = apply_rule_to_transactions(rule, fam_ids)
        assert count == 1, "One transaction should be updated."
        updated_tx = db.session.get(Transaction, tx.id)
        # confirm the rule was applied
        assert updated_tx.is_transfer is False


def test_get_transaction_field_value(app, family_user, request_context):
    from app.models.transaction import Transaction

    with app.app_context():
        # 1) Find a seeded AccountType row for the same family
        seeded_acct_type = AccountType.query.filter_by(name="Chase Checking", family_id=family_user.family_id).first()
        assert seeded_acct_type, "No seeded 'Chase Checking' AccountType found for user's family."

        cat = Category(name="AnyCat", family_id=family_user.family_id)
        db.session.add(cat)
        db.session.commit()

        tx = Transaction(
            user_id=family_user.id,
            description="Test Description",
            amount=200.0,
            category_id=cat.id,
            account_id=seeded_acct_type.id,
            is_transfer=False
        )
        db.session.add(tx)
        db.session.commit()

        val_desc = get_transaction_field_value(tx, "description")
        assert val_desc == "Test Description"

        val_cat = get_transaction_field_value(tx, "category")
        assert val_cat == "AnyCat"


def test_rules_are_family_specific_service(app, family_user, request_context):
    with app.app_context():
        rule_fam = ImportRule(
            account_type="Chase Checking",
            field_to_match="Description",
            match_pattern="FAM123",
            is_transfer=False,
            family_id=family_user.family_id
        )
        db.session.add(rule_fam)
        db.session.commit()

        rule_other = ImportRule(
            account_type="Chase Checking",
            field_to_match="Description",
            match_pattern="FAM999",
            is_transfer=False,
            family_id=999
        )
        db.session.add(rule_other)
        db.session.commit()

        same_fam_rules = ImportRule.query.filter_by(family_id=family_user.family_id).all()
        assert any(r.match_pattern == "FAM123" for r in same_fam_rules)
        assert all(r.match_pattern != "FAM999" for r in same_fam_rules)

        other_fam_rules = ImportRule.query.filter_by(family_id=999).all()
        assert any(r.match_pattern == "FAM999" for r in other_fam_rules)
        assert all(r.match_pattern != "FAM123" for r in other_fam_rules)
