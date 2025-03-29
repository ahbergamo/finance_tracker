def test_help_page(client):
    """
    Test that the help page loads successfully and contains expected content.
    """
    response = client.get("/help")
    assert response.status_code == 200
    # Check for a keyword that you expect to be on the help page, for example "Quick Start" or "User Guide".
    # Adjust the expected text based on your actual help.html template.
    assert b"Quick Start" in response.data or b"FRacker" in response.data
