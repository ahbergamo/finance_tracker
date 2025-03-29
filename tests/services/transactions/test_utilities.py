import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from flask import Flask
from sqlalchemy import create_engine
from app.services.transactions.utilities import (
    get_family_user_ids,
    create_or_get_category,
    apply_date_filter,
)


# --- Dummy classes for testing ---
class DummyUser:
    def __init__(self, id, family_id=None):
        self.id = id
        self.family_id = family_id


class DummyCategory:
    def __init__(self, name, family_id):
        self.name = name
        self.family_id = family_id


class DummyCategoryQuery:
    def __init__(self, category_obj=None):
        self.category_obj = category_obj

    def filter_by(self, **kwargs):
        if self.category_obj and kwargs.get("name") == self.category_obj.name and kwargs.get("family_id") == self.category_obj.family_id:
            return self
        self.category_obj = None
        return self

    def first(self):
        return self.category_obj


class DummyUserQuery:
    def __init__(self, users):
        self.users = users

    def filter_by(self, **kwargs):
        family_id = kwargs.get("family_id")
        filtered = [user for user in self.users if user.family_id == family_id]
        dummy = MagicMock()
        dummy.all.return_value = filtered
        return dummy


class DummySession:
    def __init__(self):
        self.add_called_with = None
        self.commit_called = False
        self.rollback_called = False

    def add(self, obj):
        self.add_called_with = obj

    def commit(self):
        self.commit_called = True

    def rollback(self):
        self.rollback_called = True


# A dummy query class that records filter calls.
class DummyQuery:
    def __init__(self):
        self.filters = []

    def filter(self, *args, **kwargs):
        self.filters.append(("filter", args, kwargs))
        return self


# --- Begin Test Class ---
class TestUtilities(unittest.TestCase):
    def setUp(self):
        # Set up a minimal Flask app context.
        self.app = Flask("test_app")
        self.app.config["SECRET_KEY"] = "testsecret"
        # To avoid issues with Flask-Login's login_manager, assign a dummy login_manager.
        self.app.login_manager = MagicMock()
        self.app_context = self.app.app_context()
        self.app_context.push()
        # Create an in-memory SQLite engine for compiling SQLAlchemy expressions.
        self.engine = create_engine("sqlite://")

    def tearDown(self):
        self.app_context.pop()

    @patch("app.services.transactions.utilities.current_app")
    @patch("app.services.transactions.utilities.current_user")
    @patch("app.services.transactions.utilities.User")
    def test_get_family_user_ids_with_family(self, mock_User, mock_current_user, mock_current_app):
        dummy_user = DummyUser(id=10, family_id=1)
        mock_current_user.id = dummy_user.id
        mock_current_user.family_id = dummy_user.family_id
        # Force the logger to be a synchronous MagicMock.
        mock_current_app.logger = MagicMock()

        user1 = DummyUser(id=10, family_id=1)
        user2 = DummyUser(id=20, family_id=1)
        dummy_users = [user1, user2]
        mock_User.query.filter_by.return_value.all.return_value = dummy_users

        ids = get_family_user_ids()
        self.assertEqual(ids, [10, 20])
        mock_current_app.logger.debug.assert_called()

    @patch("app.services.transactions.utilities.current_app")
    @patch("app.services.transactions.utilities.current_user")
    @patch("app.services.transactions.utilities.Category")
    @patch("app.services.transactions.utilities.db")
    def test_create_or_get_category_existing(self, mock_db, mock_Category, mock_current_user, mock_current_app):
        dummy_category = DummyCategory(name="Food", family_id=1)
        query_mock = DummyCategoryQuery(dummy_category)
        mock_Category.query.filter_by.return_value = query_mock
        mock_current_user.family_id = 1
        mock_current_app.logger = MagicMock()

        category_obj = create_or_get_category("Food")
        self.assertEqual(category_obj, dummy_category)
        mock_current_app.logger.debug.assert_called()

    @patch("app.services.transactions.utilities.current_app")
    @patch("app.services.transactions.utilities.current_user")
    @patch("app.services.transactions.utilities.db")
    def test_create_or_get_category_new(self, mock_db, mock_current_user, mock_current_app):
        with patch("app.services.transactions.utilities.Category", new=DummyCategory):
            DummyCategory.query = DummyCategoryQuery(None)
            mock_current_user.family_id = 1
            mock_current_app.logger = MagicMock()

            category_obj = create_or_get_category("Utilities")
            self.assertIsNotNone(category_obj)
            self.assertEqual(category_obj.name, "Utilities")
            self.assertEqual(category_obj.family_id, 1)
            mock_db.session.commit.assert_called()
            mock_current_app.logger.info.assert_called()

    def test_create_or_get_category_exception(self):
        with self.app.test_request_context("/"):
            dummy_user = DummyUser(id=100, family_id=1)
            with patch("app.services.transactions.utilities.db") as mock_db, \
                 patch("app.services.transactions.utilities.current_app") as mock_current_app, \
                 patch("app.services.transactions.utilities.current_user", new=dummy_user):
                mock_current_app.login_manager = MagicMock()
                mock_current_app.logger = MagicMock()
                mock_db.session.commit.side_effect = Exception("DB error")
                category_obj = create_or_get_category("Groceries")
                self.assertIsNone(category_obj)
                mock_db.session.rollback.assert_called()
                mock_current_app.logger.error.assert_called()

    def test_apply_date_filter_valid_end(self):
        dummy_query = DummyQuery()
        date_str = "2025-03-31"
        expected_date = datetime.strptime(date_str, "%Y-%m-%d")
        new_query = apply_date_filter(dummy_query, date_str, "end")
        self.assertTrue(len(dummy_query.filters) > 0)
        condition = dummy_query.filters[0][1][0]
        compiled = condition.compile(dialect=self.engine.dialect, compile_kwargs={"literal_binds": True})
        self.assertIn(expected_date.strftime("%Y-%m-%d"), str(compiled))
        self.assertEqual(new_query, dummy_query)

    @patch("app.services.transactions.utilities.flash")
    @patch("app.services.transactions.utilities.current_app")
    def test_apply_date_filter_invalid(self, mock_current_app, mock_flash):
        dummy_query = MagicMock()
        invalid_date = "not-a-date"
        mock_current_app.logger = MagicMock()
        new_query = apply_date_filter(dummy_query, invalid_date, "start")
        mock_current_app.logger.error.assert_called()
        mock_flash.assert_called_with("Invalid start date format.", "danger")
        self.assertEqual(new_query, dummy_query)


if __name__ == "__main__":
    unittest.main()
