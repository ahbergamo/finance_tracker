import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from types import SimpleNamespace
from app.services.transactions.delete_transaction import get_transaction_by_id, delete_transaction_from_db


# Dummy transaction class for testing.
class DummyTransaction:
    def __init__(self, id):
        self.id = id


class TestDeleteTransactionService(unittest.TestCase):
    def setUp(self):
        # Create a minimal Flask app context.
        self.app = Flask("test_app")
        self.app.config["SECRET_KEY"] = "testsecret"
        self.app_context = self.app.app_context()
        self.app_context.push()
        # Set up a dummy current_user.
        self.dummy_user = SimpleNamespace(id=100)

    def tearDown(self):
        self.app_context.pop()

    @patch("app.services.transactions.delete_transaction.get_family_user_ids", return_value=[100, 200, 300])
    @patch("app.services.transactions.delete_transaction.Transaction")
    @patch("app.services.transactions.delete_transaction.current_user")
    @patch("app.services.transactions.delete_transaction.current_app")
    def test_get_transaction_by_id_found(self, mock_current_app, mock_current_user, mock_Transaction, mock_get_family_user_ids):
        # Arrange
        mock_current_user.id = self.dummy_user.id
        logger = MagicMock()
        mock_current_app.logger = logger

        # Set up the query chain: .filter(...).first() returns a dummy transaction.
        dummy_tx = DummyTransaction(id=123)
        query_mock = MagicMock()
        query_mock.first.return_value = dummy_tx
        mock_Transaction.query.filter.return_value = query_mock

        # Act
        result = get_transaction_by_id(123)

        # Assert
        self.assertEqual(result, dummy_tx)
        logger.debug.assert_called()  # ensure logging occurred

    @patch("app.services.transactions.delete_transaction.get_family_user_ids", return_value=[100, 200, 300])
    @patch("app.services.transactions.delete_transaction.Transaction")
    @patch("app.services.transactions.delete_transaction.current_user")
    @patch("app.services.transactions.delete_transaction.current_app")
    def test_get_transaction_by_id_not_found(self, mock_current_app, mock_current_user, mock_Transaction, mock_get_family_user_ids):
        # Arrange
        mock_current_user.id = self.dummy_user.id
        logger = MagicMock()
        mock_current_app.logger = logger

        # Simulate no transaction found.
        query_mock = MagicMock()
        query_mock.first.return_value = None
        mock_Transaction.query.filter.return_value = query_mock

        # Act
        result = get_transaction_by_id(999)

        # Assert
        self.assertIsNone(result)
        logger.warning.assert_called()  # warning should be logged when transaction not found

    @patch("app.services.transactions.delete_transaction.db")
    @patch("app.services.transactions.delete_transaction.current_app")
    @patch("app.services.transactions.delete_transaction.current_user")
    def test_delete_transaction_from_db_success(self, mock_current_user, mock_current_app, mock_db):
        # Arrange: create a dummy transaction.
        dummy_tx = DummyTransaction(id=456)
        mock_current_user.id = self.dummy_user.id
        logger = MagicMock()
        mock_current_app.logger = logger

        # Act
        delete_transaction_from_db(dummy_tx)

        # Assert that the transaction is deleted and commit is called.
        mock_db.session.delete.assert_called_with(dummy_tx)
        mock_db.session.commit.assert_called_once()
        logger.info.assert_called()

    @patch("app.services.transactions.delete_transaction.db")
    @patch("app.services.transactions.delete_transaction.current_app")
    @patch("app.services.transactions.delete_transaction.current_user")
    def test_delete_transaction_from_db_exception(self, mock_current_user, mock_current_app, mock_db):
        # Arrange: create a dummy transaction.
        dummy_tx = DummyTransaction(id=789)
        mock_current_user.id = self.dummy_user.id
        logger = MagicMock()
        mock_current_app.logger = logger

        # Simulate exception during commit.
        mock_db.session.commit.side_effect = Exception("DB error")

        # Act
        delete_transaction_from_db(dummy_tx)

        # Assert: verify that rollback is called and error is logged.
        mock_db.session.delete.assert_called_with(dummy_tx)
        mock_db.session.rollback.assert_called_once()
        logger.error.assert_called()


if __name__ == "__main__":
    unittest.main()
