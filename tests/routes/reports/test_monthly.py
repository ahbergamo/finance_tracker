from tests.routes.utils import login


def test_monthly_spending_report(client):
    """
    Test that the monthly spending report loads correctly when a date range is provided.
    Instead of using a 'year' filter, we pass specific start_date and end_date parameters.
    """
    # Log in as the seeded user.
    login(client, "user1", "test123")

    # Use a specific date range for the report.
    params = "start_date=2022-01-01&end_date=2022-12-31"
    response = client.get(f"/reports/monthly?{params}", follow_redirects=True)
    assert response.status_code == 200

    # Check for the expected page title.
    assert b"Monthly Spending Report" in response.data

    # Verify that a canvas element exists (indicating that the chart is rendered).
    assert b"<canvas" in response.data
