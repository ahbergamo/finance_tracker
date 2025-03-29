import io
import csv
from app.models.transaction import Transaction
from app.models.user import User
from app.models.category import Category
from tests.routes.utils import login
from app import db


def test_add_transaction_get(client):
    """Ensure the Add Transaction page loads correctly."""
    login(client, "user1", "test123")
    response = client.get("/transactions/add")
    assert response.status_code == 200
    assert b"Add Transaction" in response.data or b"Transaction" in response.data


def test_add_transaction_post(client):
    """Test adding a new transaction."""
    login(client, "user1", "test123")
    data = {
        "amount": "123.45",
        "description": "Test Transaction",
        # Passing a string as a category name; the route will create or get the category.
        "category_id": "TestCategory",
        "account_id": "1"
    }
    response = client.post("/transactions/add", data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Transaction added successfully." in response.data
    with client.application.app_context():
        user = User.query.filter_by(username="user1").first()
        tx = Transaction.query.filter_by(user_id=user.id, description="Test Transaction").first()
        assert tx is not None


def test_edit_transaction(client):
    """Test editing an existing transaction."""
    login(client, "user1", "test123")
    # Add a transaction to edit.
    data = {
        "amount": "300.00",
        "description": "Transaction To Edit",
        "category_id": "EditCategory",  # This will create a category with name "EditCategory"
        "account_id": "1"
    }
    client.post("/transactions/add", data=data, follow_redirects=True)

    # Retrieve the transaction ID.
    with client.application.app_context():
        user = User.query.filter_by(username="user1").first()
        tx = Transaction.query.filter_by(user_id=user.id, description="Transaction To Edit").first()
        assert tx is not None, "Transaction should have been added"
        tx_id = tx.id
        # Ensure the category exists and get its numeric id.
        category = Category.query.filter_by(name="EditCategory", family_id=user.family_id).first()
        assert category is not None, "EditCategory should exist"
        valid_category_id = str(category.id)

    # Get the edit form.
    response = client.get(f"/transactions/edit/{tx_id}")
    assert response.status_code == 200
    assert b"Transaction To Edit" in response.data

    # Submit edited data using the valid numeric category id.
    edit_data = {
        "amount": "350.00",
        "description": "Transaction Edited",
        "category_id": valid_category_id,  # Use the numeric id now.
        "account_id": "1",
        "is_transfer": ""  # Not marking as transfer.
    }
    response = client.post(f"/transactions/edit/{tx_id}", data=edit_data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Transaction updated successfully." in response.data
    with client.application.app_context():
        updated_tx = db.session.get(Transaction, tx_id)
        assert updated_tx.description == "Transaction Edited"
        assert float(updated_tx.amount) == 350.00


def test_delete_transaction(client):
    """Test deleting a transaction."""
    login(client, "user1", "test123")
    data = {
        "amount": "150.00",
        "description": "Transaction To Delete",
        "category_id": "DeleteCategory",
        "account_id": "1"
    }
    client.post("/transactions/add", data=data, follow_redirects=True)
    with client.application.app_context():
        user = User.query.filter_by(username="user1").first()
        tx = Transaction.query.filter_by(user_id=user.id, description="Transaction To Delete").first()
        assert tx is not None, "Transaction to delete should exist"
        tx_id = tx.id

    response = client.post(f"/transactions/delete/{tx_id}", follow_redirects=True)
    assert response.status_code == 200
    assert b"Transaction deleted successfully." in response.data
    with client.application.app_context():
        deleted_tx = db.session.get(Transaction, tx_id)
        assert deleted_tx is None


def test_bulk_delete_transactions(client):
    """
    Test the bulk delete functionality.
    For simplicity, add two transactions and then delete them via bulk delete.
    """
    login(client, "user1", "test123")
    for desc in ["Bulk Delete 1", "Bulk Delete 2"]:
        data = {
            "amount": "50.00",
            "description": desc,
            "category_id": "BulkCategory",
            "account_id": "1"
        }
        client.post("/transactions/add", data=data, follow_redirects=True)
    response = client.get("/transactions?filter=normal", follow_redirects=True)
    assert response.status_code == 200
    with client.application.app_context():
        user = User.query.filter_by(username="user1").first()
        txs = Transaction.query.filter(Transaction.user_id == user.id, Transaction.description.like("Bulk Delete%")).all()
        ids = [str(tx.id) for tx in txs]
        assert len(ids) >= 2
    delete_data = {"transaction_ids": ids}
    response = client.post("/transactions/bulk_delete", data=delete_data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Deleted" in response.data
    with client.application.app_context():
        for tx_id in ids:
            tx = db.session.get(Transaction, int(tx_id))
            assert tx is None


def test_download_csv(client):
    """Test that the CSV download route returns a CSV file with expected header."""
    login(client, "user1", "test123")
    response = client.get("/transactions/download?filter=normal", follow_redirects=True)
    assert response.status_code == 200
    content_disp = response.headers.get("Content-Disposition")
    assert "filename=transactions.csv" in content_disp
    content = response.data.decode("utf-8")
    reader = csv.reader(io.StringIO(content))
    header = next(reader)
    expected_header = ["Date", "Description", "Amount", "Account Type", "Category"]
    assert header == expected_header


def test_transactions_family_isolation(client):
    """
    Verify that transactions are only visible to members of the same family.
    A transaction added by a member of one family should not be visible to a member of another.
    """
    # Log in as "user1" (Family_1 family).
    login(client, "user1", "test123")
    data = {
        "amount": "999.99",
        "description": "Family Isolation Test",
        "category_id": "IsolationCategory",
        "account_id": "1"
    }
    client.post("/transactions/add", data=data, follow_redirects=True)
    client.get("/logout", follow_redirects=True)
    # Log in as "frank" (from Awesome family).
    login(client, "frank", "asdded123")
    response = client.get("/transactions", follow_redirects=True)
    # Verify that the transaction does not appear.
    assert b"Family Isolation Test" not in response.data
