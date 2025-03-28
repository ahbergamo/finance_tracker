import datetime
import pytest
from app import db
from app.models.budget import Budget
from app.models.category import Category
from app.models.user import User
from tests.routes.utils import login


@pytest.fixture(autouse=True)
def clear_budgets(app):
    """Clear all budgets before each test."""
    with app.app_context():
        db.session.query(Budget).delete()
        db.session.commit()
    yield


def test_get_budgets_page(client):
    """
    Test that the budgets page loads and displays an element like "Add Budget".
    """
    login(client, "user1", "test123")
    response = client.get("/budgets")
    assert response.status_code == 200
    # For example, your template shows a link/button "Add Budget"
    assert b"Add Budget" in response.data


def test_add_budget_success(client, app):
    """
    Test that a new budget is successfully added via the POST method.
    """
    login(client, "user1", "test123")
    with app.app_context():
        # Retrieve the seeded user "user1"
        user = User.query.filter_by(username="user1").first()
        assert user is not None, "Seeded user 'user1' should exist."

        # Ensure a category exists; if not, create it.
        category = Category.query.filter_by(name="TestBudgetCat", family_id=user.family_id).first()
        if not category:
            category = Category(name="TestBudgetCat", family_id=user.family_id)
            db.session.add(category)
            db.session.commit()
        valid_category_id = str(category.id)  # Form data is sent as strings

    # When posting the form, note that getlist() returns a list.
    # (Our route calls add_budget with a keyword argument 'category_ids'.)
    budget_data = {
        "name": "Test Budget",
        "amount": "1000.00",
        "start_date": "2025-01-01",
        "end_date": "2025-12-31",
        "category_ids": [valid_category_id]
    }
    response = client.post("/budgets", data=budget_data, follow_redirects=True)
    # Expect a success flash message on the redirected page
    assert b"Budget added successfully." in response.data

    # Verify that the budget was added to the database.
    with app.app_context():
        budget = Budget.query.filter_by(name="Test Budget").first()
        assert budget is not None, "Budget should have been added."
        assert float(budget.amount) == 1000.00


def test_add_budget_invalid_date(client, app):
    """
    Test that a budget is not added when provided with an invalid start_date.
    """
    login(client, "user1", "test123")
    with app.app_context():
        user = User.query.filter_by(username="user1").first()
        assert user is not None, "Seeded user 'user1' should exist."
        # Ensure a category exists.
        category = Category.query.filter_by(name="TestBudgetCat", family_id=user.family_id).first()
        if not category:
            category = Category(name="TestBudgetCat", family_id=user.family_id)
            db.session.add(category)
            db.session.commit()
        valid_category_id = str(category.id)

    # Provide an invalid start_date format.
    budget_data = {
        "name": "Invalid Budget",
        "amount": "500.00",
        "start_date": "invalid-date",
        "end_date": "2025-12-31",
        "category_ids": [valid_category_id]
    }
    response = client.post("/budgets", data=budget_data, follow_redirects=True)
    # Expect a failure flash message
    assert b"Failed to add budget." in response.data


def test_delete_budget(client, app):
    """
    Test that an existing budget can be deleted.
    """
    login(client, "user1", "test123")
    with app.app_context():
        user = User.query.filter_by(username="user1").first()
        assert user is not None
        # Create a budget to delete.
        budget = Budget(
            name="Budget To Delete",
            amount=500.00,
            start_date=datetime.date(2025, 1, 1),
            end_date=datetime.date(2025, 12, 31),
            user_id=user.id
        )
        db.session.add(budget)
        db.session.commit()
        budget_id = budget.id

    response = client.post(f"/budgets/delete/{budget_id}", follow_redirects=True)
    assert b"Budget deleted successfully." in response.data
    # Verify deletion
    with app.app_context():
        deleted = db.session.get(Budget, budget_id)
        assert deleted is None


def test_edit_budget(client, app):
    """
    Test that an existing budget can be edited.
    """
    login(client, "user1", "test123")
    with app.app_context():
        user = User.query.filter_by(username="user1").first()
        assert user is not None
        # Ensure a category exists.
        category = Category.query.filter_by(name="TestBudgetCat", family_id=user.family_id).first()
        if not category:
            category = Category(name="TestBudgetCat", family_id=user.family_id)
            db.session.add(category)
            db.session.commit()
        # Create a budget to edit.
        budget = Budget(
            name="Budget To Edit",
            amount=750.00,
            start_date=datetime.date(2025, 1, 1),
            end_date=datetime.date(2025, 12, 31),
            user_id=user.id,
            # Assume that budgets have a many-to-many relationship with categories.
            categories=[category]
        )
        db.session.add(budget)
        db.session.commit()
        budget_id = budget.id

    # GET the edit page.
    response = client.get(f"/budgets/edit/{budget_id}")
    assert response.status_code == 200
    assert b"Budget To Edit" in response.data

    # POST updated data.
    edit_data = {
        "name": "Edited Budget",
        "amount": "800.00",
        "start_date": "2025-01-01",
        "end_date": "2025-12-31",
        "category_ids": [str(category.id)]
    }
    response = client.post(f"/budgets/edit/{budget_id}", data=edit_data, follow_redirects=True)
    assert b"Budget updated successfully." in response.data

    # Verify that the budget is updated in the database.
    with app.app_context():
        edited = db.session.get(Budget, budget_id)
        assert edited.name == "Edited Budget"
        assert float(edited.amount) == 800.00
