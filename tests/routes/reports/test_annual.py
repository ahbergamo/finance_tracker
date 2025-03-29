from tests.routes.utils import login


def test_annual_overview(client):
    """
    Test that the annual overview report loads correctly with valid filters.
    """
    # Log in as a seeded user (e.g., "user1" with password "test123")
    login(client, "user1", "test123")
    # Request the annual overview report with a specified date range.
    response = client.get("/reports/annual?start_date=2022-01-01&end_date=2022-12-31", follow_redirects=True)
    assert response.status_code == 200
    # Check that the response data contains an expected year (e.g., "2022")
    assert b"2022" in response.data or b"Annual" in response.data
