import pytest
from app import db
from app.models.budget import Budget
from app.models.category import Category
from app.models.user import User
from app.services.budget import add_budget, edit_budget, delete_budget


# Fixture to clear budgets before (and after) tests
@pytest.fixture
def clear_budgets(app):
    with app.app_context():
        db.session.query(Budget).delete()
        db.session.commit()
    yield
    with app.app_context():
        db.session.query(Budget).delete()
        db.session.commit()


# Fixture for a test category; assumes a family_id of the seeded user
@pytest.fixture
def test_category(app):
    with app.app_context():
        # Create or retrieve a category named "TestBudgetCat" for testing.
        category = Category.query.filter_by(name="TestBudgetCat").first()
        if not category:
            # Here we assume a family_id of 1 for testing; adjust as needed.
            category = Category(name="TestBudgetCat", family_id=1)
            db.session.add(category)
            db.session.commit()
        yield category
        # Optionally delete the test category after test runs
        # db.session.delete(category)
        # db.session.commit()


# Fixture for a seeded user (e.g. "user1"); ensure your test database has that user.
@pytest.fixture
def test_user(app):
    with app.app_context():
        user = User.query.filter_by(username="user1").first()
        if not user:
            pytest.skip("Seeded user 'user1' not found.")
        yield user


def test_add_budget_success(app, clear_budgets, test_user, test_category):
    """
    Test that add_budget successfully adds a new budget.
    """
    with app.app_context():
        # Call the service function. Note that category_ids is passed as a list of ints.
        result = add_budget(
            user_id=test_user.id,
            name="Test Budget",
            category_ids=[test_category.id],
            amount="1000.00",
            start_date="2025-01-01",
            end_date="2025-12-31"
        )
        assert result is True, "add_budget should return True on success"
        # Verify the budget was added
        budget = Budget.query.filter_by(name="Test Budget", user_id=test_user.id).first()
        assert budget is not None
        assert budget.amount == 1000.00
        # Verify that the budget is linked to the test category
        assert len(budget.categories) == 1
        assert budget.categories[0].id == test_category.id


def test_edit_budget_success(app, clear_budgets, test_user, test_category):
    """
    Test that edit_budget correctly updates an existing budget.
    """
    with app.app_context():
        # First, add a budget to update.
        add_result = add_budget(
            user_id=test_user.id,
            name="Original Budget",
            category_ids=[test_category.id],
            amount="500.00",
            start_date="2025-01-01",
            end_date="2025-06-30"
        )
        assert add_result is True
        budget = Budget.query.filter_by(name="Original Budget", user_id=test_user.id).first()
        assert budget is not None

        # Create a new category to update to.
        new_category = Category(name="NewBudgetCat", family_id=test_category.family_id)
        db.session.add(new_category)
        db.session.commit()

        # Call the edit service to update the budget.
        edit_result = edit_budget(
            budget=budget,
            name="Updated Budget",
            category_ids=[new_category.id],
            amount="750.00",
            start_date="2025-02-01",
            end_date="2025-07-31"
        )
        assert edit_result is True, "edit_budget should return True on success"

        updated_budget = Budget.query.filter_by(id=budget.id).first()
        assert updated_budget.name == "Updated Budget"
        assert updated_budget.amount == 750.00
        # Check that the categories have been updated.
        assert len(updated_budget.categories) == 1
        assert updated_budget.categories[0].id == new_category.id

        # Clean up the new category.
        db.session.delete(new_category)
        db.session.commit()


def test_delete_budget_success(app, clear_budgets, test_user, test_category):
    """
    Test that delete_budget successfully deletes a budget.
    """
    with app.app_context():
        # Add a budget to be deleted.
        add_result = add_budget(
            user_id=test_user.id,
            name="Budget To Delete",
            category_ids=[test_category.id],
            amount="600.00",
            start_date="2025-03-01",
            end_date="2025-09-30"
        )
        assert add_result is True
        budget = Budget.query.filter_by(name="Budget To Delete", user_id=test_user.id).first()
        assert budget is not None

        # Call the delete service.
        delete_result = delete_budget(budget)
        assert delete_result is True, "delete_budget should return True on success"
        # Verify the budget no longer exists.
        deleted_budget = Budget.query.filter_by(id=budget.id).first()
        assert deleted_budget is None
