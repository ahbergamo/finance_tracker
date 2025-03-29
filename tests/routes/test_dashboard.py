from tests.routes.utils import login


def test_dashboard_view(client):
    """
    Test that the dashboard loads and displays expected elements.
    """
    # Log in as a seeded user ("user1" with password "test123")
    login(client, "user1", "test123")

    response = client.get("/dashboard")
    assert response.status_code == 200
    # Check for some text that should appear on the dashboard.
    # For example, if your template renders "FRacker" in the navbar or header.
    assert b"FRacker" in response.data
    # Optionally, check for financial data labels
    assert b"Total Income" in response.data or b"Income" in response.data


def test_set_chart_slices(client):
    """
    Test that updating chart slice settings via POST to /set_chart_slices
    updates the session and redirects back to the dashboard with a flash message.
    """
    # Log in as a seeded user.
    login(client, "user1", "test123")

    # Send a POST request with a new income chart slice setting.
    data = {"top_n_income": "5"}
    response = client.post("/set_chart_slices", data=data, follow_redirects=True)

    assert response.status_code == 200
    # Check that the success flash message is present.
    assert b"Income chart slice settings updated." in response.data


# Additional tests for other aspects of the dashboard (e.g. totals, monthly data, etc.)
# could be added here following a similar pattern.
