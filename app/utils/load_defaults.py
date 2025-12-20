
from flask import current_app
from app.models.pre_defined_account import PreDefinedAccount
from app.models.category import Category
from app.constants.account_types import DEFAULT_ACCOUNT_TYPES
from app import db

# Default retirement-related categories
DEFAULT_RETIREMENT_CATEGORIES = [
    "401k Contribution",
    "401k Employer Match",
    "Traditional IRA Contribution",
    "Roth IRA Contribution",
    "403b Contribution",
    "403b Employer Match",
    "HSA Contribution",
    "Retirement Account Transfer",
    "Retirement Investment",
    "Retirement Withdrawal"
]


def ensure_default_account_types():
    for entry in DEFAULT_ACCOUNT_TYPES:
        if not PreDefinedAccount.query.filter_by(name=entry["name"]).first():
            db.session.add(PreDefinedAccount(**entry))
    db.session.commit()


def ensure_default_retirement_categories(family_id):
    """Create default retirement categories for a family if they don't exist."""
    for category_name in DEFAULT_RETIREMENT_CATEGORIES:
        if not Category.query.filter_by(name=category_name, family_id=family_id).first():
            category = Category(name=category_name, family_id=family_id)
            db.session.add(category)
    db.session.commit()


if __name__ == "__main__":
    from app import create_app
    app = create_app()
    with app.app_context():
        print("App context active, current_app:", current_app.name)
        ensure_default_account_types()
