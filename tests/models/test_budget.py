import pytest
from datetime import date
from app import db
from app.models.budget import Budget
from app.models.category import Category
from app.models.user import User


def get_seeded_user():
    """
    Returns a seeded user. For this example we assume that a user with
    username "user1" is available from the seed script.
    """
    user = User.query.filter_by(username="user1").first()
    if not user:
        pytest.skip("Seeded user 'user1' not found.")
    return user


def get_seeded_category():
    """
    Returns a seeded category. For this example we assume that a category named
    "Credit Card Payment" exists because it is created in the seed script.
    """
    category = Category.query.filter_by(name="Credit Card Payment").first()
    if not category:
        pytest.skip("Seeded category 'Credit Card Payment' not found.")
    return category


def test_budget_category_association(app):
    """
    Verify that a budget can be associated with a seeded category via the
    many-to-many relationship.
    """
    user = get_seeded_user()
    category = get_seeded_category()

    # Create a new budget using the seeded user.
    budget = Budget(
        name="Test Budget",
        amount=1000.0,
        start_date=date(2025, 1, 1),
        end_date=date(2025, 12, 31),
        user_id=user.id
    )
    db.session.add(budget)
    db.session.commit()

    # Associate the seeded category with the new budget.
    budget.categories.append(category)
    db.session.commit()

    # Verify the association from the Budget side.
    assert category in budget.categories, "Seeded category not associated with Budget"

    # Verify the reverse relationship, if defined.
    assert budget in category.budgets, "Budget not reflected in Category's relationship"


def test_budget_remove_category(app):
    """
    Verify that removing a category from a budget updates the association correctly.
    """
    user = get_seeded_user()
    category = get_seeded_category()

    # Create a budget and add the seeded category.
    budget = Budget(
        name="Budget Remove Test",
        amount=2000.0,
        start_date=date(2025, 2, 1),
        end_date=date(2025, 11, 30),
        user_id=user.id
    )
    db.session.add(budget)
    db.session.commit()

    budget.categories.append(category)
    db.session.commit()
    assert category in budget.categories, "Category should be associated initially."

    # Remove the category and verify.
    budget.categories.remove(category)
    db.session.commit()
    assert category not in budget.categories, "Category removal did not update association."


def test_budget_multiple_categories(app):
    """
    Verify that a budget can be associated with multiple categories.
    Here we attempt to use two seeded categories if available.
    """
    user = get_seeded_user()

    # Query for two seeded categories. We know one, so try for a second.
    category1 = get_seeded_category()
    category2 = Category.query.filter(Category.name != "Credit Card Payment").first()
    if not category2:
        pytest.skip("A second seeded category was not found.")

    budget = Budget(
        name="Multi-Category Budget",
        amount=3000.0,
        start_date=date(2025, 3, 1),
        end_date=date(2025, 9, 30),
        user_id=user.id
    )
    db.session.add(budget)
    db.session.commit()

    # Associate both categories.
    budget.categories.extend([category1, category2])
    db.session.commit()

    # Verify that both categories are linked.
    assert len(budget.categories) == 2, "Budget should be associated with two categories."
    assert category1 in budget.categories, "First category not associated."
    assert category2 in budget.categories, "Second category not associated."
