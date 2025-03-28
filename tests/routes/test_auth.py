def test_get_login(client):
    """
    Ensure the login page is accessible.
    """
    response = client.get("/login")
    assert response.status_code == 200
    # Look for an element that should be on the login page.
    assert b"Username" in response.data


def test_register_and_logout(client, app):
    """
    Test user registration followed by logout.

    This test uses the seeded database as a baseline.
    """
    # Simulate a POST to register a new user.
    reg_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "family_name": "NewFamily",
        "password": "Test@123",
        "confirm_password": "Test@123"
    }
    response = client.post("/register", data=reg_data, follow_redirects=True)
    # After a successful registration, the user should be redirected to the dashboard.
    assert response.status_code == 200
    assert b"Dashboard" in response.data or b"dashboard" in response.data

    # Now test logging out.
    response = client.get("/logout", follow_redirects=True)
    # After logout, we should be sent back to the login page.
    assert response.status_code == 200
    assert b"Login" in response.data


def test_change_password(client, app):
    """
    Test the change password flow.

    Uses the seeded user "user1" with password "test123" from your seed script.
    """
    # First, log in with the seeded user.
    login_data = {
        "username": "user1",
        "password": "test123"
    }
    response = client.post("/login", data=login_data, follow_redirects=True)
    assert response.status_code == 200
    # Verify that login was successful (e.g., dashboard content appears)
    assert b"Dashboard" in response.data or b"dashboard" in response.data

    # Access the change password form.
    response = client.get("/change_password")
    assert response.status_code == 200
    assert b"Current Password" in response.data

    # Attempt to change the password with an incorrect current password.
    wrong_data = {
        "current_password": "incorrect",
        "new_password": "NewTest@123",
        "confirm_new_password": "NewTest@123"
    }
    response = client.post("/change_password", data=wrong_data, follow_redirects=True)
    assert response.status_code == 200
    # Expect an error message regarding the incorrect current password.
    assert b"Incorrect current password" in response.data

    # Now change the password with the correct current password.
    correct_data = {
        "current_password": "test123",
        "new_password": "NewTest@123",
        "confirm_new_password": "NewTest@123"
    }
    response = client.post("/change_password", data=correct_data, follow_redirects=True)
    # Successful change should redirect the user to the login page.
    assert response.status_code == 200
    assert b"Login" in response.data
