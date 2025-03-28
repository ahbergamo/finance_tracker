import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from types import SimpleNamespace
from app.services.transactions.bulk_delete import (
    build_transaction_query,
    delete_all_transactions,
    delete_selected_transactions,
    handle_post_request,
    render_bulk_delete_page,
)


# Dummy query that behaves like a real query.
class DummyTransactionQuery:
    def __init__(self):
        self.deleted_count = 0

    def filter(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def paginate(self, page, per_page, error_out):
        return SimpleNamespace(
            items=[{"id": 1, "timestamp": "dummy_timestamp"}],
            page=page,
            per_page=per_page,
            total=1
        )

    def delete(self, synchronize_session="fetch"):
        # Simulate deletion by updating deleted_count.
        self.deleted_count = 5
        return self.deleted_count


# Dummy classes to simulate Category and AccountType queries.
class DummyCategory:
    @classmethod
    def query(cls):
        return cls

    @classmethod
    def filter_by(cls, **kwargs):
        dummy = MagicMock()
        dummy.order_by.return_value.all.return_value = ["Cat1", "Cat2"]
        return dummy


class DummyAccountType:
    @classmethod
    def query(cls):
        return cls

    @classmethod
    def filter_by(cls, **kwargs):
        dummy = MagicMock()
        dummy.order_by.return_value.all.return_value = ["Acc1", "Acc2"]
        return dummy


# A dummy apply_date_filter that returns the query unchanged.
def dummy_apply_date_filter(query, date_str, filter_type):
    return query


class TestBulkDeleteService(unittest.TestCase):
    def setUp(self):
        self.app = Flask("test_app")
        self.app.config["SECRET_KEY"] = "testsecret"
        self.app.config["SERVER_NAME"] = "localhost"
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_build_transaction_query(self):
        # Use a request context so that request.args is available.
        with self.app.test_request_context(
            "/bulk_delete?start_date=2024-01-01&end_date=2024-12-31&category_id=1&account_id=2"
        ):
            with patch("app.services.transactions.bulk_delete.Transaction") as mock_Transaction:
                mock_query = DummyTransactionQuery()
                mock_Transaction.query.filter.return_value = mock_query
                query, filters = build_transaction_query([1, 2, 3])
                self.assertEqual(filters["start_date"], "2024-01-01")
                self.assertEqual(filters["end_date"], "2024-12-31")
                self.assertEqual(filters["category_id"], 1)
                self.assertEqual(filters["account_id"], 2)

    @patch("app.services.transactions.bulk_delete.url_for", return_value="/bulk_delete")
    @patch("app.services.transactions.bulk_delete.flash")
    @patch("app.services.transactions.bulk_delete.db")
    def test_delete_all_transactions_success(self, mock_db, mock_flash, mock_url_for):
        dummy_query = DummyTransactionQuery()  # use our proper dummy query
        with self.app.test_request_context("/bulk_delete"):
            result = delete_all_transactions(dummy_query)
            self.assertEqual(result.status_code, 302)
            self.assertEqual(result.location, "/bulk_delete")
            # Now check that our dummy_query's delete() method updated deleted_count to 5.
            self.assertEqual(dummy_query.deleted_count, 5)
            mock_db.session.commit.assert_called_once()
            mock_flash.assert_called_once_with("Deleted all 5 matching transactions.", "success")

    @patch("app.services.transactions.bulk_delete.url_for", return_value="/bulk_delete")
    @patch("app.services.transactions.bulk_delete.flash")
    @patch("app.services.transactions.bulk_delete.db")
    @patch("app.services.transactions.bulk_delete.Transaction")
    def test_delete_selected_transactions_success(self, mock_Transaction, mock_db, mock_flash, mock_url_for):
        with self.app.test_request_context("/bulk_delete", method="POST", data={"transaction_ids": ["1", "2", "3"]}):
            dummy_query = DummyTransactionQuery()
            mock_Transaction.query.filter.return_value = dummy_query
            dummy_query.delete = lambda synchronize_session="fetch": 3
            filters = {}
            result = delete_selected_transactions(filters)
            self.assertEqual(result.status_code, 302)
            self.assertIn("/bulk_delete", result.location)
            # Here we check the return value from delete().
            self.assertEqual(dummy_query.delete(synchronize_session="fetch"), 3)
            mock_db.session.commit.assert_called_once()
            mock_flash.assert_called_once_with("Deleted 3 transactions.", "success")

    @patch("app.services.transactions.bulk_delete.delete_all_transactions")
    @patch("app.services.transactions.bulk_delete.delete_selected_transactions")
    def test_handle_post_request_delete_all(self, mock_delete_selected, mock_delete_all):
        form_data = {"delete_all": "true"}
        with self.app.test_request_context("/bulk_delete", method="POST", data=form_data):
            dummy_query = DummyTransactionQuery()
            filters = {"start_date": None, "end_date": None, "category_id": None, "account_id": None}
            mock_delete_all.return_value = "redirect_all"
            result = handle_post_request(dummy_query, filters)
            mock_delete_all.assert_called_with(dummy_query)
            self.assertEqual(result, "redirect_all")

    @patch("app.services.transactions.bulk_delete.render_template", return_value="bulk_delete_page")
    @patch("app.services.transactions.bulk_delete.Category")
    @patch("app.services.transactions.bulk_delete.AccountType")
    def test_render_bulk_delete_page_success(self, mock_AccountType, mock_Category, mock_render_template):
        with self.app.test_request_context("/bulk_delete?page=2"):
            filters = {
                "start_date": "2023-01-01",
                "end_date": "2023-01-31",
                "category_id": 5,
                "account_id": 10
            }
            dummy_query = DummyTransactionQuery()
            mock_Category.query.filter_by.return_value.order_by.return_value.all.return_value = ["Cat1", "Cat2"]
            mock_AccountType.query.filter_by.return_value.order_by.return_value.all.return_value = ["Acc1", "Acc2"]
            result = render_bulk_delete_page(dummy_query, filters)
            mock_render_template.assert_called()
            self.assertEqual(result, "bulk_delete_page")


if __name__ == "__main__":
    unittest.main()
