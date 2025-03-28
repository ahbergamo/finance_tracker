import pytest
from unittest.mock import patch, MagicMock
from werkzeug.datastructures import MultiDict
from app.services.reports.annual import (
    parse_filters,
    get_family_user_ids,
    build_query,
    get_dropdown_options
)
from app.models.user import User


def test_parse_filters_no_args(app):
    with app.app_context():
        request_args = MultiDict({})
        filters = parse_filters(request_args)
        assert filters['start_date'] is None
        assert filters['end_date'] is None
        assert filters['category_id'] is None
        assert filters['account_id'] is None


def test_parse_filters_with_args(app):
    with app.app_context():
        request_args = MultiDict({
            'start_date': '2023-01-01',
            'end_date': '2023-12-31',
            'category_id': '5',
            'account_id': '10'
        })
        filters = parse_filters(request_args)
        assert filters['start_date'] == '2023-01-01'
        assert filters['end_date'] == '2023-12-31'
        # MultiDict’s get(..., type=int) will convert these to int
        assert filters['category_id'] == 5
        assert filters['account_id'] == 10


@pytest.mark.parametrize("family_id, expected_ids", [
    (None, [123]),
    (999, [111, 222])
])
@patch("app.services.reports.annual.User")
def test_get_family_user_ids(mock_user_class, family_id, expected_ids, app):
    with app.app_context():
        current_user = User(id=123, family_id=family_id)
        query_mock = MagicMock()
        if family_id:
            query_mock.with_entities.return_value.filter_by.return_value.all.return_value = [
                (uid,) for uid in expected_ids
            ]
        else:
            query_mock.with_entities.return_value.filter_by.return_value.all.return_value = []
        mock_user_class.query = query_mock
        result = get_family_user_ids(current_user)
        assert result == expected_ids


@patch("app.services.reports.annual.db.session.query")
def test_build_query(mock_query, app):
    with app.app_context():
        filters = {
            'start_date': '2023-01-01',
            'end_date': '2023-01-31',
            'category_id': 10,
            'account_id': 20
        }
        family_user_ids = [111, 222]
        current_user = User(id=999)
        query_instance = MagicMock()
        query_instance.filter.return_value = query_instance
        query_instance.group_by.return_value = query_instance
        query_instance.order_by.return_value = query_instance
        mock_query.return_value = query_instance

        returned_query = build_query(filters, family_user_ids, current_user)
        assert returned_query is query_instance
        mock_query.assert_called_once()


@patch("app.services.reports.annual.Category.query", new_callable=MagicMock)
@patch("app.services.reports.annual.AccountType.query", new_callable=MagicMock)
def test_get_dropdown_options(mock_account_query, mock_category_query, app):
    """
    The added 'app' parameter (from your conftest.py) ensures an active application context.
    """
    with app.app_context():
        current_user = User(id=123, family_id=999)
        mock_category_query.filter_by.return_value.all.return_value = ["cat1", "cat2"]
        mock_account_query.filter_by.return_value.all.return_value = ["acct1", "acct2"]

        cats, accts = get_dropdown_options(current_user)
        assert cats == ["cat1", "cat2"]
        assert accts == ["acct1", "acct2"]
        mock_category_query.filter_by.assert_called_once_with(family_id=999)
        mock_account_query.filter_by.assert_called_once_with(family_id=999)
