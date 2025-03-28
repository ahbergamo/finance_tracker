# tests/seed_test_data.py

from app import db
from app.models.user import User
from app.models.family import Family
from app.models.account_type import AccountType
from app.models.import_rule import ImportRule
from app.models.category import Category
from app.utils.load_defaults import ensure_default_account_types


def seed_db_for_tests():
    """Seed the database with fake data for tests."""

    # Load default account settings (if your app needs it)
    ensure_default_account_types()

    # Helper function to get or create a category for a given family.
    def get_or_create_category(category_name, family_id):
        category = Category.query.filter_by(name=category_name, family_id=family_id).first()
        if not category:
            category = Category(name=category_name, family_id=family_id)
            db.session.add(category)
            db.session.commit()
        return category

    # ------------------
    # SEED FOR FAMILY #1: 'Family_1'
    # ------------------
    family1 = Family(name='Family_1')
    db.session.add(family1)
    db.session.commit()  # Commit to generate family1.id

    # Seed two fake users
    user1 = User(username='user1', email='user1@example.com', family_id=family1.id)
    user1.set_password('test123')  # hashed
    db.session.add(user1)

    user2 = User(username='user2', email='user2@example.com', family_id=family1.id)
    user2.set_password('test456')  # hashed
    db.session.add(user2)
    db.session.commit()

    # Seed account types
    account_types1 = [
        AccountType(
            name="Chase Prime Credit",
            category_field="Category",
            date_field="Transaction Date",
            amount_field="Amount",
            description_field="Description",
            family_id=family1.id,
            positive_expense=False
        ),
        AccountType(
            name="Chase Checking",
            category_field="Type",
            date_field="Posting Date",
            amount_field="Amount",
            description_field="Description",
            family_id=family1.id,
            positive_expense=False
        ),
        AccountType(
            name="Chase Savings",
            category_field="Type",
            date_field="Posting Date",
            amount_field="Amount",
            description_field="Description",
            family_id=family1.id,
            positive_expense=False
        ),
        AccountType(
            name="Discover Credit",
            category_field="Category",
            date_field="Trans. Date",
            amount_field="Amount",
            description_field="Description",
            family_id=family1.id,
            positive_expense=True
        ),
    ]
    db.session.bulk_save_objects(account_types1)
    db.session.commit()

    # Seed import rules with override_category_id from get_or_create_category
    import_rules1 = [
        ImportRule(
            account_type="Chase Prime Credit",
            field_to_match="Description",
            match_pattern="Payment Thank You - Web",
            is_transfer=True,
            override_category_id=get_or_create_category("Credit Card Payment", family1.id).id,
            family_id=family1.id
        ),
        ImportRule(
            account_type="Chase Checking",
            field_to_match="Description",
            match_pattern="Payment to Chase card",
            is_transfer=True,
            override_category_id=get_or_create_category("Credit Card Payment", family1.id).id,
            family_id=family1.id
        ),
        ImportRule(
            account_type="Chase Checking",
            field_to_match="Description",
            match_pattern="DISCOVER",
            is_transfer=True,
            override_category_id=get_or_create_category("Credit Card Payment", family1.id).id,
            family_id=family1.id
        ),
        # ... etc. for other patterns ...
    ]
    db.session.bulk_save_objects(import_rules1)
    db.session.commit()

    # ------------------
    # SEED FOR FAMILY #2: 'Awesome'
    # ------------------
    family2 = Family(name='Awesome')
    db.session.add(family2)
    db.session.commit()  # Generate family2.id

    # Seed another fake user
    user3 = User(username='frank', email='franke@example.com', family_id=family2.id)
    user3.set_password('asdded123')
    db.session.add(user3)
    db.session.commit()

    # Example account types for family2
    account_types2 = [
        AccountType(
            name="US Bank Checking",
            category_field="Transaction",
            date_field="Date",
            amount_field="Amount",
            description_field="Name",
            family_id=family2.id,
            positive_expense=False
        ),
        AccountType(
            name="US Bank Savings",
            category_field="Type",
            date_field="Posting Date",
            amount_field="Amount",
            description_field="Description",
            family_id=family2.id,
            positive_expense=False
        ),
        AccountType(
            name="Discover Credit",
            category_field="Category",
            date_field="Trans. Date",
            amount_field="Amount",
            description_field="Description",
            family_id=family2.id,
            positive_expense=True
        )
    ]
    db.session.bulk_save_objects(account_types2)
    db.session.commit()

    import_rules2 = [
        ImportRule(
            account_type="Discover Credit",
            field_to_match="Description",
            match_pattern="PAYMENT - THANK YOU",
            is_transfer=True,
            override_category_id=get_or_create_category("Credit Card Payment", family2.id).id,
            family_id=family2.id
        ),
        ImportRule(
            account_type="US Bank Checking",
            field_to_match="Description",
            match_pattern="FEDERAL BENEFIT CREDIT",
            is_transfer=False,
            override_category_id=get_or_create_category("Social Security", family2.id).id,
            family_id=family2.id
        ),
        ImportRule(
            account_type="US Bank Checking",
            field_to_match="Description",
            match_pattern="ELECTRONIC DEPOSIT PUB",
            is_transfer=False,
            override_category_id=get_or_create_category("Pension", family2.id).id,
            family_id=family2.id
        ),
    ]
    db.session.bulk_save_objects(import_rules2)
    db.session.commit()

    print("Database seeded with fake test data.")
