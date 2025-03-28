import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from calendar import monthrange
from flask import Flask
from types import SimpleNamespace
from app.services.transactions.main import (
    apply_time_filter,
    calculate_summary,
    apply_filters,
    process_transactions_view,
)


# --- Dummy Query Class ---
class DummyQuery:
    def __init__(self):
        self.filters = []
        self.deleted_count = 0

    def filter(self, *args, **kwargs):
        self.filters.append(("filter", args, kwargs))
        return self

    def order_by(self, *args, **kwargs):
        self.filters.append(("order_by", args, kwargs))
        return self

    def paginate(self, page, per_page, error_out):
        return SimpleNamespace(
            items=[{"id": 1, "timestamp": datetime(2025, 3, 15)}],
            page=page,
            per_page=per_page,
            total=1
        )

    def with_entities(self, *args, **kwargs):
        self.with_entities_called = True
        dummy_summary = SimpleNamespace(total_count=10, total_income=1000, total_expense=-500)
        dummy_summary.first = lambda: dummy_summary
        return dummy_summary

    def delete(self, synchronize_session="fetch"):
        self.deleted_count = 3
        return self.deleted_count


# --- Dummy Models for Category and AccountType ---
class DummyCategoryModel:
    pass


DummyCategoryModel.query = MagicMock()
DummyCategoryModel.query.filter_by.return_value.order_by.return_value.all.return_value = ["Cat1", "Cat2"]


class DummyAccountTypeModel:
    pass


DummyAccountTypeModel.query = MagicMock()
DummyAccountTypeModel.query.filter_by.return_value.order_by.return_value.all.return_value = ["Acc1", "Acc2"]


# Dummy get_family_user_ids function.
def dummy_get_family_user_ids():
    return [100, 200, 300]


class TestMainService(unittest.TestCase):
    def setUp(self):
        self.app = Flask("test_app")
        self.app.config["SECRET_KEY"] = "test_secret"
        self.app_context = self.app.app_context()
        self.app_context.push()
        # Dummy current_user for testing
        self.dummy_user = SimpleNamespace(id=100, family_id=1)

    def tearDown(self):
        self.app_context.pop()

    def test_apply_time_filter_month(self):
        now = datetime.now()
        start_date = datetime(now.year, now.month, 1)
        last_day = monthrange(now.year, now.month)[1]
        end_date = datetime(now.year, now.month, last_day)
        expected_display = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        dummy_query = DummyQuery()
        with self.app.test_request_context():
            query, date_range_display = apply_time_filter(dummy_query, "month")
            self.assertEqual(date_range_display, expected_display)
            self.assertTrue(len(dummy_query.filters) >= 1)

    def test_calculate_summary(self):
        dummy_query = DummyQuery()
        with self.app.test_request_context():
            summary = calculate_summary(dummy_query)
            self.assertIsNotNone(summary)
            self.assertEqual(summary.total_count, 10)
            self.assertEqual(summary.total_income, 1000)
            self.assertEqual(summary.total_expense, -500)
            self.assertTrue(hasattr(dummy_query, "with_entities_called"))

    def test_apply_filters(self):
        dummy_query = DummyQuery()
        filtered_query = apply_filters(dummy_query, category_id=5, category_ids=None, account_id=2)
        self.assertEqual(filtered_query, dummy_query)

    @patch("app.services.transactions.main.get_family_user_ids", side_effect=dummy_get_family_user_ids)
    @patch("app.services.transactions.main.Category", new=DummyCategoryModel)
    @patch("app.services.transactions.main.AccountType", new=DummyAccountTypeModel)
    @patch("app.services.transactions.main.calculate_summary", return_value="dummy_summary")
    @patch("app.services.transactions.main.apply_filters", side_effect=lambda q, cid, cids, aid: q)
    @patch("app.services.transactions.main.apply_time_filter", side_effect=lambda q, tf: (q, "dummy_range"))
    def test_process_transactions_view_non_duplicates(self, mock_apply_time_filter, mock_apply_filters, mock_calculate_summary, mock_get_family):
        dummy_query = DummyQuery()
        with self.app.test_request_context("/transactions/main?page=1"):
            filter_type = "income"
            time_filter = "month"
            category_id = 5
            category_ids = None
            account_id = 2
            page = 1
            per_page = 20
            with patch("app.services.transactions.main.Transaction") as mock_Transaction:
                # Make sure Transaction.amount is a numeric value.
                mock_Transaction.amount = 1
                mock_Transaction.query.filter.return_value = dummy_query
                with patch("app.services.transactions.main.current_user", self.dummy_user):
                    result = process_transactions_view(filter_type, time_filter, category_id, category_ids, account_id, page, per_page)
            expected_keys = {"transactions", "account_types", "selected_account", "categories",
                             "selected_category", "filter_type", "time_filter", "pagination",
                             "date_range_display", "summary"}
            self.assertEqual(set(result.keys()), expected_keys)
            self.assertEqual(result["date_range_display"], "dummy_range")
            self.assertEqual(result["summary"], "dummy_summary")

    @patch("app.services.transactions.main.handle_duplicates", return_value=({}, "dup_summary"))
    @patch("app.services.transactions.main.get_family_user_ids", side_effect=dummy_get_family_user_ids)
    @patch("app.services.transactions.main.Category", new=DummyCategoryModel)
    @patch("app.services.transactions.main.AccountType", new=DummyAccountTypeModel)
    def test_process_transactions_view_duplicates(self, mock_get_family, mock_handle_duplicates):
        with self.app.test_request_context("/transactions/main?page=1"):
            filter_type = "duplicates"
            time_filter = "month"
            category_id = 5
            category_ids = None
            account_id = 2
            page = 1
            per_page = 20
            with patch("app.services.transactions.main.current_user", self.dummy_user):
                result = process_transactions_view(filter_type, time_filter, category_id, category_ids, account_id, page, per_page)
                expected_keys = {"grouped_duplicates", "account_types", "selected_account", "categories",
                                 "selected_category", "filter_type", "time_filter", "pagination",
                                 "date_range_display", "summary"}
                self.assertEqual(set(result.keys()), expected_keys)
                self.assertEqual(result["date_range_display"], "Duplicate Transactions")
                self.assertEqual(result["summary"], "dup_summary")


if __name__ == "__main__":
    unittest.main()
