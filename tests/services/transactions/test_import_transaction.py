import io
import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import patch
from werkzeug.datastructures import MultiDict
from app.services.transactions.import_transaction import process_file_upload


# Dummy account type object to simulate a valid account type
class DummyAccountType:
    id = 1
    name = "Checking"
    date_field = "Date"
    description_field = "Description"
    amount_field = "Amount"
    category_field = "Category"
    positive_expense = False
    family_id = 1


# Dummy file object to simulate an uploaded CSV file in Flask
class DummyFile:
    def __init__(self, filename, content):
        self.filename = filename
        # Flask's file object has a stream attribute that is a file-like object.
        self.stream = io.BytesIO(content.encode('utf-8'))


# Dummy container to simulate Flask's req.files MultiDict
class DummyFiles:
    def __init__(self, files):
        self.files = files

    def getlist(self, key):
        # For our test, we assume the key is "csv_file" and return our list of dummy files.
        return self.files


def dummy_parse_csv(file, acc_type_obj, delimiter=","):
    """
    Dummy parse_csv that returns a list with one tuple.
    """
    # Simulate a single CSV row: (tx_date, description, amount, category_name)
    return [(datetime(2023, 1, 1), "Test Transaction", 100.0, "Test Category")]


def dummy_apply_import_rules(transactions_data, acc_type_obj):
    """
    Dummy apply_import_rules that returns a list of processed transactions.
    """
    # Create a dummy processed transaction dictionary
    return [{
        "tx_date": "01/01/2023",
        "amount": 100.0,
        "description": "Test Transaction",
        "category_field": "Test Category",
        "account_id": acc_type_obj.id,
        "account_name": acc_type_obj.name,
        "is_duplicate": False,
        "tx_key": (datetime(2023, 1, 1).date(), 100.0),
        "is_transfer": False,
        "force_import": False
    }]


class TestImportTransactionService(unittest.TestCase):

    @patch("app.services.transactions.import_transaction.prepare_import_preview")
    @patch("app.services.transactions.import_transaction.check_duplicate", return_value=False)
    @patch("app.services.transactions.import_transaction.apply_import_rules", side_effect=dummy_apply_import_rules)
    @patch("app.services.transactions.import_transaction.parse_csv", side_effect=dummy_parse_csv)
    @patch("app.services.transactions.import_transaction.get_account_type", return_value=DummyAccountType())
    def test_process_file_upload_valid_file(self, mock_get_account_type, mock_parse_csv, mock_apply_import_rules, mock_check_duplicate, mock_prepare_import_preview):

        # Arrange: Create a dummy CSV file content and a dummy request object.
        csv_content = "Date,Description,Amount,Category\n2023-01-01,Test Transaction,100,Test Category\n"
        dummy_file = DummyFile("test.csv", csv_content)
        # Use DummyFiles to simulate req.files with getlist.
        dummy_files = DummyFiles([dummy_file])
        # Use MultiDict to simulate Flask's req.form which supports type conversion.
        form = MultiDict({"account_id": "1"})
        req = SimpleNamespace(
            form=form,
            files=dummy_files
        )
        # Simulate current_user with minimal required attributes.
        current_user = SimpleNamespace(id=1, family_id=1)

        # Prepare the preview page to be returned.
        mock_prepare_import_preview.return_value = "preview_page"

        # Act: Call the process_file_upload function from the service.
        result = process_file_upload(req, current_user)

        # Assert: Ensure that the preview page is returned and that our dummy functions were called.
        self.assertEqual(result, "preview_page")
        mock_get_account_type.assert_called_once_with(1, current_user)
        mock_parse_csv.assert_called_once()  # Called for our dummy file.
        mock_apply_import_rules.assert_called_once()
        # check_duplicate should be called at least once for the processed transaction.
        mock_check_duplicate.assert_called()
        mock_prepare_import_preview.assert_called_once()


if __name__ == "__main__":
    unittest.main()
