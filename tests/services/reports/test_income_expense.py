import pytest
from datetime import datetime, date
from unittest.mock import patch, MagicMock
from werkzeug.datastructures import MultiDict
from app.services.reports.income_expense import (
    get_date_filters,
    parse_date_range,
    get_family_user_ids,
    build_transaction_query,
    process_transaction_results,
    get_cached_categories,
    get_cached_accounts
)
from app.models.user import User


def test_get_date_filters_no_args(app):
    with app.app_context():
        request_args = MultiDict({})
        start_date, end_date = get_date_filters(request_args)
        assert start_date is not None
        assert end_date is not None


def test_parse_date_range_valid(app):
    with app.app_context():
        start_dt, end_dt = parse_date_range('2023-01-01', '2023-02-01')
        assert start_dt == datetime(2023, 1, 1)
        assert end_dt == datetime(2023, 2, 1)


def test_parse_date_range_invalid(app):
    with app.app_context():
        start_dt, end_dt = parse_date_range('invalid-date', 'invalid-date')
        assert isinstance(start_dt, (datetime, date))
        assert isinstance(end_dt, (datetime, date))


@pytest.mark.parametrize("family_id, expected_ids", [
    (None, [123]),
    (999, [111, 222])
])
@patch("app.services.reports.income_expense.User")
def test_get_family_user_ids(mock_user_class, family_id, expected_ids, app):
    with app.app_context():
        current_user = User(id=123, family_id=family_id)
        query_mock = MagicMock()
        if family_id:
            query_mock.filter_by.return_value.all.return_value = [
                User(id=uid) for uid in expected_ids
            ]
        else:
            query_mock.filter_by.return_value.all.return_value = []
        mock_user_class.query = query_mock
        result = get_family_user_ids(current_user)
        assert result == expected_ids


@patch("app.services.reports.income_expense.db.session.query")
def test_build_transaction_query(mock_query, app):
    with app.app_context():
        user_ids = [111, 222]
        start_dt = datetime(2023, 1, 1)
        end_dt = datetime(2023, 1, 31)
        query_instance = MagicMock()
        query_instance.filter.return_value = query_instance
        mock_query.return_value = query_instance
        returned_query = build_transaction_query(user_ids, start_dt, end_dt, category_id=10, account_id=20)
        assert returned_query is query_instance
        mock_query.assert_called_once()


def test_process_transaction_results(app):
    with app.app_context():
        # Create dummy row objects to simulate SQLAlchemy row objects.
        class DummyRow:
            def __init__(self, year, month, income, expense):
                self.year = year
                self.month = month
                self.income = income
                self.expense = expense

        dummy_results = [
            DummyRow(2023, 1, 500.0, -100.0),
            DummyRow(2023, 2, 1000.0, -200.0),
        ]

        class DummyQuery:

            def with_entities(self, *args, **kwargs):
                return self

            def group_by(self, *args, **kwargs):
                return self

            def order_by(self, *args, **kwargs):
                return self

            def all(self):
                return dummy_results

        labels, incomes, expenses = process_transaction_results(DummyQuery())
        assert labels == ["2023-01", "2023-02"]
        assert incomes == [500.0, 1000.0]
        assert expenses == [100.0, 200.0]


@patch("app.services.reports.income_expense.Category.query", new_callable=MagicMock)
@patch("app.services.reports.income_expense.AccountType.query", new_callable=MagicMock)
def test_get_cached_categories_and_accounts(mock_account_query, mock_category_query, app):
    """
    The added 'app' parameter ensures an active application context.
    """
    with app.app_context():
        current_user = User(id=1, family_id=999)
        mock_category_query.filter_by.return_value.all.return_value = ["catA", "catB"]
        mock_account_query.filter_by.return_value.all.return_value = ["acctA", "acctB"]

        categories = get_cached_categories(current_user)
        accounts = get_cached_accounts(current_user)
        assert categories == ["catA", "catB"]
        assert accounts == ["acctA", "acctB"]
