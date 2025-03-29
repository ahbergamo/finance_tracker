import pytest
from datetime import date
from app import db
from app.models.category import Category
from app.models.family import Family
from app.models.budget import Budget
from app.models.user import User


def get_seeded_category():
    """
    Retrieve a seeded category.
    Assumes a category with name 'Credit Card Payment' exists.
    """
    category = Category.query.filter_by(name="Credit Card Payment").first()
    if not category:
        pytest.skip("Seeded category 'Credit Card Payment' not found.")
    return category


def get_seeded_family():
    """
    Retrieve a seeded family.
    Assumes a family with name 'Family_1' exists.
    """
    family = Family.query.filter_by(name="Family_1").first()
    if not family:
        pytest.skip("Seeded family 'Family_1' not found.")
    return family


def get_seeded_user():
    """
    Retrieve a seeded user.
    Assumes a user with username 'user1' exists.
    """
    user = User.query.filter_by(username="user1").first()
    if not user:
        pytest.skip("Seeded user 'user1' not found.")
    return user


def test_category_repr(app):
    """
    Verify that the __repr__ method returns the expected string.
    """
    category = get_seeded_category()
    expected = f"<Category {category.name} (Family ID: {category.family_id})>"
    assert repr(category) == expected


def test_category_uniqueness(app):
    """
    Verify that creating two categories with the same name and family_id
    violates the unique constraint.
    """
    family = get_seeded_family()

    # Create a new category with a unique name.
    category1 = Category(name="UniqueTestCategory", family_id=family.id)
    db.session.add(category1)
    db.session.commit()

    # Attempt to create another category with the same name and family_id.
    category2 = Category(name="UniqueTestCategory", family_id=family.id)
    db.session.add(category2)
    with pytest.raises(Exception):
        db.session.commit()
    db.session.rollback()


def test_category_budget_relationship(app):
    """
    Verify that a budget can be associated with a seeded category,
    and that the relationship is reflected on both sides.
    """
    category = get_seeded_category()
    user = get_seeded_user()

    # Create a new budget using the seeded user.
    budget = Budget(
        name="Category Relation Budget",
        amount=500.0,
        start_date=date(2025, 4, 1),
        end_date=date(2025, 4, 30),
        user_id=user.id
    )
    db.session.add(budget)
    db.session.commit()

    # Associate the budget with the seeded category.
    category.budgets.append(budget)
    db.session.commit()

    # Verify the association from the Category side.
    assert budget in category.budgets, "Budget was not associated with the Category."

    # Also verify the reverse relationship if defined (Budget.categories).
    assert category in budget.categories, "Category not reflected in Budget's relationship."
