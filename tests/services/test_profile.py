import uuid
from app import db
from app.models.user import User
from app.models.family import Family
from app.services.profile import (
    update_user_profile,
    get_family_name_for_user,
    get_or_create_family
)


def _unique_username(base="testuser"):
    """
    Generate a unique username to avoid collisions with seed data,
    e.g. testuser_46e3b2a1.
    """
    return f"{base}_{uuid.uuid4().hex[:8]}"


def test_get_or_create_family_creates_new_family(app):
    """
    Test that get_or_create_family creates a new family if it doesn't exist.
    """
    with app.app_context():
        new_family_name = "TestFamilyXYZ"
        existing = Family.query.filter_by(name=new_family_name).first()
        assert existing is None

        family = get_or_create_family(new_family_name)
        assert family is not None
        assert family.name == new_family_name

        # Calling again should return the same family, not create a new one
        same_family = get_or_create_family(new_family_name)
        assert same_family.id == family.id
        assert Family.query.filter_by(name=new_family_name).count() == 1


def test_get_family_name_for_user_no_family(app):
    """
    If the user has no family_id, get_family_name_for_user should return "".
    """
    with app.app_context():
        user = User(
            username=_unique_username("no_family"),
            email="no_family@example.com"
        )
        user.set_password("fake1234")
        db.session.add(user)
        db.session.commit()

        fam_name = get_family_name_for_user(user)
        assert fam_name == ""


def test_get_family_name_for_user_existing(app):
    """
    If the user belongs to a family, we should get that family's name.
    """
    with app.app_context():
        fam = get_or_create_family("MyTestFamily")
        user = User(
            username=_unique_username("famuser"),
            email="famuser@example.com",
            family_id=fam.id
        )
        user.set_password("fake1234")
        db.session.add(user)
        db.session.commit()

        fam_name = get_family_name_for_user(user)
        assert fam_name == "MyTestFamily"


def test_update_user_profile_no_family(app):
    """
    Test updating a user's username/email without specifying a family_name.
    """
    with app.app_context():
        # Create a user with a unique username
        user = User(
            username=_unique_username("profile_no_family"),
            email="nofamily@example.com"
        )
        user.set_password("fakePassword")
        db.session.add(user)
        db.session.commit()

        success = update_user_profile(
            user=user,
            username="UpdatedName",
            email="updated@example.com",
            family_name=None
        )
        assert success is True, "Expected update to succeed"

        updated_user = db.session.get(User, user.id)
        assert updated_user.username == "UpdatedName"
        assert updated_user.email == "updated@example.com"
        assert updated_user.family_id is None


def test_update_user_profile_with_family(app):
    """
    Test updating a user's profile when the family name field is disabled.
    The family name update should be ignored, so the user's family remains unchanged.
    """
    with app.app_context():
        # Create a user with an existing family.
        # For this test, we'll first create a family and assign it to the user.
        original_family = get_or_create_family("OriginalFamily")
        user = User(
            username=_unique_username("profile_with_family"),
            email="withfamily@example.com",
            family_id=original_family.id
        )
        user.set_password("fakePassword")
        db.session.add(user)
        db.session.commit()

        # Attempt to update the profile with a new username/email,
        # but we disable the family name update by passing None.
        success = update_user_profile(
            user=user,
            username="NewName",
            email="new@example.com",
            # "family_name" field is disabled so we pass None or omit it
            family_name=None
        )
        assert success is True

        updated_user = db.session.get(User, user.id)
        assert updated_user.username == "NewName"
        assert updated_user.email == "new@example.com"
        # The family should remain unchanged.
        assert updated_user.family_id == original_family.id

        fam = db.session.get(Family, original_family.id)
        assert fam is not None
        assert fam.name == "OriginalFamily"
        # Ensure no new family with the updated name was created.
        assert Family.query.filter_by(name="UpdatedFamily").first() is None


def test_update_user_profile_rollback_on_error(app, monkeypatch):
    """
    Demonstrate forcing an error and ensuring rollback happens.
    In this case, the family update is disabled.
    """
    from app.services.profile import update_user_profile

    def mock_commit_raises():
        raise Exception("Forced DB error")

    with app.app_context():
        user = User(
            username=_unique_username("rollback"),
            email="rollback@example.com"
        )
        user.set_password("fake1234")
        db.session.add(user)
        db.session.commit()

        # Force an exception on db.session.commit
        monkeypatch.setattr(db.session, "commit", mock_commit_raises)

        success = update_user_profile(
            user=user,
            username="BreakMe",
            email="break@example.com",
            # Family update is disabled
            family_name=None
        )
        assert success is False, "Should return False on error"

        # The update should have been rolled back
        reverted_user = db.session.get(User, user.id)
        assert reverted_user.username != "BreakMe"
        assert reverted_user.email != "break@example.com"

        # Since family update was disabled, no family should have been created.
        fam = Family.query.filter_by(name="RollbackFam").first()
        assert fam is None
