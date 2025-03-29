from app.models.user import User
from app.models.family import Family
from tests.routes.utils import login
from app import db


def test_get_profile(client):
    """
    Test that the profile page loads and prepopulates with the current user's data.
    """
    # Log in as the seeded user "user1"
    login(client, "user1", "test123")
    response = client.get("/profile")
    assert response.status_code == 200
    # Check that the rendered form contains the current username.
    assert b"user1" in response.data


def test_update_profile_creates_new_family(client):
    """
    Test updating the profile with a new family name would create a new family,
    but since the family field is disabled, the family update is ignored.
    """
    # Log in as the seeded user "user1"
    login(client, "user1", "test123")

    # Prepare new profile data: change username and email.
    # The family_name update is now commented out because the field is disabled.
    update_data = {
        "username": "newuser1",
        "email": "newuser1@example.com",
        # "family_name": "NewFamily"
    }
    response = client.post("/profile", data=update_data, follow_redirects=True)
    assert response.status_code == 200
    # Verify the flash message indicating success.
    assert b"Profile updated successfully." in response.data

    # Verify that the updated profile reflects the new username.
    response = client.get("/profile")
    assert b"newuser1" in response.data

    # Verify in the database that the user's family remains unchanged.
    with client.application.app_context():
        user = User.query.filter_by(username="newuser1").first()
        assert user is not None, "User should exist after update."
        # Since the family update is disabled, we expect the family to remain as it was.
        family = db.session.get(Family, user.family_id)
        assert family is not None, "Family should still exist for the user."
        # Optionally, you could check that the family name is not "NewFamily"
        # assert family.name != "NewFamily", "Family name should not be updated."


def test_update_profile_without_family_change(client):
    """
    Test that updating the profile without changing the family name leaves the family unchanged.
    """
    # Log in as "user1"
    login(client, "user1", "test123")

    # First, fetch current family name.
    with client.application.app_context():
        user = User.query.filter_by(username="user1").first()
        original_family_id = user.family_id
        original_family_name = ""
        if original_family_id:
            from app.models.family import Family
            family = db.session.get(Family, original_family_id)
            original_family_name = family.name if family else ""

    # Update profile data without changing the family name.
    update_data = {
        "username": "user1_updated",
        "email": "user1_updated@example.com",
        "family_name": original_family_name  # keeping the same family name
    }
    response = client.post("/profile", data=update_data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Profile updated successfully." in response.data

    # Verify the username update.
    response = client.get("/profile")
    assert b"user1_updated" in response.data

    # Verify that the family ID remains unchanged.
    with client.application.app_context():
        updated_user = User.query.filter_by(username="user1_updated").first()
        assert updated_user is not None
        assert updated_user.family_id == original_family_id, "Family ID should remain unchanged."
