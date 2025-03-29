import pytest
from app import db
from app.models.pre_defined_account import PreDefinedAccount


def test_predefined_account_repr(app):
    """
    Verify that the __repr__ method returns the expected string.
    """
    account = PreDefinedAccount(
        name="Test PreDefined Account",
        category_field="Category",
        date_field="Transaction Date",
        amount_field="Amount",
        description_field="Test Description",
        positive_expense=True
    )
    db.session.add(account)
    db.session.commit()

    expected = f"<PreDefinedAccount {account.name}>"
    assert repr(account) == expected


def test_predefined_account_unique_constraint(app):
    """
    Verify that creating two PreDefinedAccount instances with the same name
    violates the unique constraint.
    """
    account1 = PreDefinedAccount(
        name="UniqueAccount",
        category_field="Category",
        date_field="Transaction Date",
        amount_field="Amount",
        description_field="Test Description",
        positive_expense=False
    )
    db.session.add(account1)
    db.session.commit()

    account2 = PreDefinedAccount(
        name="UniqueAccount",  # Same name as account1
        category_field="Other Category",
        date_field="Other Date",
        amount_field="Other Amount",
        description_field="Other Description",
        positive_expense=True
    )
    db.session.add(account2)
    with pytest.raises(Exception):
        db.session.commit()
    db.session.rollback()
