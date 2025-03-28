def test_index_redirects_to_login(client):
    # When a non-authenticated user visits the root route,
    # they should be redirected to the login page.
    response = client.get("/")
    assert response.status_code == 302
    # Verify that the redirect URL contains "/login"
    assert "/login" in response.location
