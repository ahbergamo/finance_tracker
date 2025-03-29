import unittest
from unittest.mock import patch, MagicMock
from werkzeug.datastructures import MultiDict
from flask import Flask
from app.services.transactions.add_transaction import process_add_transaction, render_add_transaction_form


# Dummy objects for testing.
class DummyCategory:
    name = "Food"


class DummyTransaction:
    def __init__(self, amount, description, category_id, user_id, account_id):
        self.amount = amount
        self.description = description
        self.category_id = category_id
        self.user_id = user_id
        self.account_id = account_id


class DummyUser:
    id = 1
    family_id = 1


class TestAddTransactionService(unittest.TestCase):

    @patch("app.services.transactions.add_transaction.create_or_get_category", return_value=DummyCategory())
    @patch("app.services.transactions.add_transaction.db")
    @patch("app.services.transactions.add_transaction.flash")
    def test_process_add_transaction_successful(self, mock_flash, mock_db, mock_create_or_get_category):
        # Arrange: create a dummy form using MultiDict to support type conversion.
        form = MultiDict({
            "amount": "50.0",
            "description": "Dinner at restaurant",
            "category_id": "Food",
            "account_id": "1"
        })

        dummy_user = DummyUser()
        # Set up a minimal Flask app context.
        app = Flask("test_app")
        with app.app_context():
            with patch("app.services.transactions.add_transaction.current_user", dummy_user):
                with patch("app.services.transactions.add_transaction.current_app") as mock_current_app:
                    mock_current_app.logger = MagicMock()
                    # Patch Transaction to simulate creation.
                    with patch("app.services.transactions.add_transaction.Transaction", side_effect=lambda **kwargs: DummyTransaction(**kwargs)):
                        # Act: call the function.
                        new_tx, error_flag = process_add_transaction(form)

        # Assert: the transaction should be created successfully and error_flag should be None.
        self.assertIsNotNone(new_tx)
        self.assertIsNone(error_flag)
        self.assertEqual(new_tx.amount, "50.0")
        self.assertEqual(new_tx.description, "Dinner at restaurant")
        self.assertEqual(new_tx.category_id, "Food")
        self.assertEqual(new_tx.user_id, dummy_user.id)
        self.assertEqual(new_tx.account_id, 1)
        mock_flash.assert_called_with("Transaction added successfully.", "success")
        mock_db.session.commit.assert_called()

    @patch("app.services.transactions.add_transaction.create_or_get_category", return_value=None)
    def test_process_add_transaction_category_failure(self, mock_create_or_get_category):
        # Arrange: form data where category lookup fails.
        form = MultiDict({
            "amount": "25.0",
            "description": "Snack",
            "category_id": "NonExistent",
            "account_id": "2"
        })
        dummy_user = DummyUser()
        app = Flask("test_app")
        with app.app_context():
            with patch("app.services.transactions.add_transaction.current_user", dummy_user):
                # Act: since create_or_get_category returns None, expect a redirect flag.
                new_tx, error_flag = process_add_transaction(form)
        # Assert: should return (None, "redirect")
        self.assertIsNone(new_tx)
        self.assertEqual(error_flag, "redirect")

    @patch("app.services.transactions.add_transaction.create_or_get_category", return_value=DummyCategory())
    @patch("app.services.transactions.add_transaction.db")
    @patch("app.services.transactions.add_transaction.flash")
    def test_process_add_transaction_exception(self, mock_flash, mock_db, mock_create_or_get_category):
        # Arrange: form data that will trigger an exception during commit.
        form = MultiDict({
            "amount": "100.0",
            "description": "Groceries",
            "category_id": "Food",
            "account_id": "1"
        })
        dummy_user = DummyUser()
        app = Flask("test_app")
        with app.app_context():
            with patch("app.services.transactions.add_transaction.current_user", dummy_user):
                with patch("app.services.transactions.add_transaction.current_app") as mock_current_app:
                    mock_current_app.logger = MagicMock()
                    with patch("app.services.transactions.add_transaction.Transaction",
                               side_effect=lambda **kwargs: DummyTransaction(**kwargs)):
                        mock_db.session.commit.side_effect = Exception("DB error")
                        new_tx, error_flag = process_add_transaction(form)
        # Assert: transaction should still be created locally but commit fails,
        # rollback is triggered and flash error is called.
        self.assertIsNotNone(new_tx)
        self.assertIsNone(error_flag)
        mock_db.session.rollback.assert_called()
        mock_flash.assert_called_with("An error occurred while adding the transaction. Please try again.", "danger")

    @patch("app.services.transactions.add_transaction.render_template")
    @patch("app.services.transactions.add_transaction.redirect")
    @patch("app.services.transactions.add_transaction.url_for", return_value="/transactions")
    @patch("app.services.transactions.add_transaction.Category")
    @patch("app.services.transactions.add_transaction.AccountType")
    @patch("app.services.transactions.add_transaction.flash")
    def test_render_add_transaction_form_success(self, mock_flash, mock_account_type, mock_category,
                                                 mock_url_for, mock_redirect, mock_render_template):
        # Arrange: set up dummy query return values.
        dummy_categories = ["Cat1", "Cat2"]
        dummy_accounts = ["Acc1"]
        mock_category.query.filter_by.return_value.all.return_value = dummy_categories
        mock_account_type.query.filter_by.return_value.all.return_value = dummy_accounts

        dummy_user = DummyUser()
        app = Flask("test_app")
        with app.app_context():
            with patch("app.services.transactions.add_transaction.current_user", dummy_user):
                with patch("app.services.transactions.add_transaction.current_app") as mock_current_app:
                    mock_current_app.logger = MagicMock()
                    result = render_add_transaction_form()

        mock_render_template.assert_called_with("transactions/add_transaction.html", categories=dummy_categories, account_types=dummy_accounts)
        self.assertEqual(result, mock_render_template.return_value)

    @patch("app.services.transactions.add_transaction.redirect")
    @patch("app.services.transactions.add_transaction.url_for", return_value="/transactions")
    @patch("app.services.transactions.add_transaction.Category")
    @patch("app.services.transactions.add_transaction.AccountType")
    @patch("app.services.transactions.add_transaction.flash")
    def test_render_add_transaction_form_failure(self, mock_flash, mock_account_type, mock_category,
                                                 mock_url_for, mock_redirect):
        # Arrange: simulate exception during query.
        dummy_user = DummyUser()
        app = Flask("test_app")
        with app.app_context():
            with patch("app.services.transactions.add_transaction.current_user", dummy_user):
                with patch("app.services.transactions.add_transaction.current_app") as mock_current_app:
                    mock_current_app.logger = MagicMock()
                    mock_category.query.filter_by.side_effect = Exception("Query error")
                    result = render_add_transaction_form()
        mock_flash.assert_called_with("An error occurred while loading the form. Please try again.", "danger")
        mock_redirect.assert_called_with("/transactions")
        self.assertEqual(result, mock_redirect.return_value)


if __name__ == "__main__":
    unittest.main()
