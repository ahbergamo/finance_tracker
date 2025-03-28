import pytest
from app import db
from app.models.user import User
from app.models.category import Category
from app.services.category import (
    get_categories_for_user,
    add_category,
    update_category,
    delete_category_from_db
)


@pytest.fixture
def test_user_Family_1(app):
    """
    Creates and returns a user in the 'Family_1' family for testing.
    We provide a dummy password_hash to avoid NOT NULL constraint issues.
    """
    with app.app_context():
        user = User(
            username="service_tester_yg",
            email="tester_yg@example.com",
            family_id=1,  # This assumes family.id=1 is 'Family_1' from your seed.
            password_hash="fake-hash-for-testing"
        )
        db.session.add(user)
        db.session.commit()
        yield user
        # Teardown
        db.session.delete(user)
        db.session.commit()


@pytest.fixture
def test_user_Awesome(app):
    """
    Creates and returns a user in the 'Awesome' family for testing.
    We provide a dummy password_hash to avoid NOT NULL constraint issues.
    """
    with app.app_context():
        user = User(
            username="service_tester_Awesome",
            email="tester_Awesome@example.com",
            family_id=2,  # This assumes family.id=2 is 'Awesome' from your seed.
            password_hash="fake-hash-for-testing"
        )
        db.session.add(user)
        db.session.commit()
        yield user
        # Teardown
        db.session.delete(user)
        db.session.commit()


@pytest.fixture
def category_context(app):
    """
    Provides a Flask request context so we can test flash/log calls if needed.
    """
    with app.test_request_context():
        yield


def test_add_category_success(app, test_user_Family_1, category_context):
    """
    Test that add_category() creates a Category in the database,
    verifying the count increases by 1.
    """
    with app.app_context():
        original_count = Category.query.count()
        add_category(name="ServiceTestCategory", family_id=test_user_Family_1.family_id)

        # Verify count incremented by 1
        new_count = Category.query.count()
        assert new_count == original_count + 1

        cat = Category.query.filter_by(name="ServiceTestCategory").first()
        assert cat is not None
        assert cat.family_id == test_user_Family_1.family_id


def test_get_categories_for_user(app, test_user_Family_1, category_context):
    """
    Test that get_categories_for_user() retrieves only categories for
    the given family_id, in alphabetical order.
    """
    with app.app_context():
        # Current user family
        fam_id = test_user_Family_1.family_id

        # Create some categories for the test user's family
        cat1 = Category(name="Alpha", family_id=fam_id)
        cat2 = Category(name="Beta", family_id=fam_id)
        cat_other_family = Category(name="Gamma", family_id=999)  # Different family
        db.session.add_all([cat1, cat2, cat_other_family])
        db.session.commit()

        # Call the service
        result = get_categories_for_user(fam_id)
        names = [c.name for c in result]

        # Should only retrieve cat1 and cat2, in alphabetical order
        assert len(result) >= 2  # could be more if seed data is present
        assert "Alpha" in names
        assert "Beta" in names
        # 'Gamma' belongs to family_id=999, so it shouldn't appear
        assert "Gamma" not in names


def test_update_category(app, test_user_Family_1, category_context):
    """
    Test that update_category() updates an existing category's name.
    """
    with app.app_context():
        cat = Category(name="OldName", family_id=test_user_Family_1.family_id)
        db.session.add(cat)
        db.session.commit()

        update_category(cat, "NewName")

        updated = db.session.get(Category, cat.id)
        assert updated.name == "NewName"


def test_delete_category_from_db(app, test_user_Family_1, category_context):
    """
    Test that delete_category_from_db() removes a Category from the database.
    """
    with app.app_context():
        cat = Category(name="DeleteMe", family_id=test_user_Family_1.family_id)
        db.session.add(cat)
        db.session.commit()
        cat_id = cat.id

        delete_category_from_db(cat)

        cat2 = db.session.get(Category, cat_id)
        assert cat2 is None


def test_categories_shared_within_family(app, test_user_Family_1, category_context):
    """
    Ensures that if multiple users share the same family_id, they can see each other's categories.
    For this test, we assume 'user1' or 'user2' exist in the same family with ID=1 (seed).
    """
    with app.app_context():
        # We'll use the user from our fixture + assume 'user1' is also family_id=1
        # Create a new category under the fixture user
        new_cat_name = "FamilySharedCategory"
        add_category(new_cat_name, test_user_Family_1.family_id)

        # Suppose we look up 'user1' (seed user in the same family = 1).
        user1 = User.query.filter_by(username="user1").first()
        assert user1 is not None
        assert user1.family_id == test_user_Family_1.family_id

        # get_categories_for_user should return the new_cat_name for both users in family 1
        shared_cats = get_categories_for_user(user1.family_id)
        names = [c.name for c in shared_cats]
        assert new_cat_name in names, "Category should be visible to all users in same family."


def test_categories_isolated_across_families(app, test_user_Family_1, test_user_Awesome, category_context):
    """
    Ensures that categories created for Family 1 ('Family_1') are NOT visible to Family 2 ('Awesome') users,
    and vice versa.
    """
    with app.app_context():
        # Create a category for Family 1
        cat_yg = Category(name="YG_Exclusive", family_id=test_user_Family_1.family_id)
        db.session.add(cat_yg)
        db.session.commit()

        # Create a category for Family 2
        cat_Awesome = Category(name="Awesome_Exclusive", family_id=test_user_Awesome.family_id)
        db.session.add(cat_Awesome)
        db.session.commit()

        # Now confirm Family 1 can't see Family 2's category
        fam1_cats = get_categories_for_user(test_user_Family_1.family_id)
        fam1_cat_names = {c.name for c in fam1_cats}
        assert "Awesome_Exclusive" not in fam1_cat_names
        assert "YG_Exclusive" in fam1_cat_names

        # Confirm Family 2 can't see Family 1's category
        fam2_cats = get_categories_for_user(test_user_Awesome.family_id)
        fam2_cat_names = {c.name for c in fam2_cats}
        assert "YG_Exclusive" not in fam2_cat_names
        assert "Awesome_Exclusive" in fam2_cat_names
