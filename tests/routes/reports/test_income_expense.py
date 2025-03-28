from tests.routes.utils import login


def test_income_expense_report(client):
    """
    Test that the income vs. expense report loads correctly with valid date filters.
    """
    # Log in as the seeded user.
    login(client, "user1", "test123")
    # Request the income vs. expense report with a date range.
    response = client.get("/reports/income_expense?start_date=2022-01-01&end_date=2022-12-31", follow_redirects=True)
    assert response.status_code == 200
    # Check for expected keywords in the report, such as "Income" or "Expense".
    assert b"Income" in response.data or b"Expense" in response.data
