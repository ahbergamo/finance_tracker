from flask import current_app
from app import db
from app.models.family import Family


def update_user_profile(user, username, email, family_name):
    current_app.logger.debug(
        "Updating profile for user ID %s with username='%s', email='%s', family_name='%s'",
        user.id, username, email, family_name
    )
    try:
        user.username = username.strip()
        user.email = email.strip()

        if family_name:
            current_app.logger.debug("Family name provided, processing family: %s", family_name)
            family = get_or_create_family(family_name.strip())
            if family:
                user.family_id = family.id
                current_app.logger.debug("Set user.family_id to %s", family.id)
            else:
                current_app.logger.error("Failed to get or create family for name '%s'", family_name)
        else:
            current_app.logger.debug("No family name provided for user ID %s", user.id)

        db.session.add(user)
        db.session.commit()
        current_app.logger.info("Profile updated successfully for user ID %s", user.id)
        return True
    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Error updating profile for user ID %s: %s", user.id, str(e))
        return False


def get_or_create_family(family_name):
    """
    Retrieves existing family by name or creates a new one if not found.

    Raises on DB errors, so caller should handle exceptions or do a rollback.
    """
    current_app.logger.debug("Attempting to get or create family with name '%s'", family_name)
    try:
        family = Family.query.filter_by(name=family_name).first()
        if not family:
            current_app.logger.info("Family '%s' not found. Creating new family.", family_name)
            family = Family(name=family_name)
            db.session.add(family)
            db.session.commit()
            current_app.logger.info("Created new family '%s' with ID %s", family_name, family.id)
        else:
            current_app.logger.debug("Found existing family '%s' with ID %s", family_name, family.id)
        return family
    except Exception as e:
        db.session.rollback()
        current_app.logger.error("Error handling family creation/retrieval for '%s': %s", family_name, str(e))
        raise  # Let the caller handle the error


def get_family_name_for_user(user):
    """
    Safely returns the user's family name if it exists, or an empty string.
    Logs/handles exceptions as needed.
    """
    if not user.family_id:
        current_app.logger.debug("User ID %s has no family_id", user.id)
        return ""

    current_app.logger.debug("Fetching family name for user ID %s with family_id=%s", user.id, user.family_id)
    try:
        # Use db.session instead of a generic 'session'
        family = db.session.get(Family, user.family_id)
        if family:
            current_app.logger.debug("Found family name '%s' for user ID %s", family.name, user.id)
        else:
            current_app.logger.warning("No family found for user ID %s with family_id=%s", user.id, user.family_id)
        return family.name if family else ""
    except Exception as e:
        current_app.logger.error("Error loading family for user ID %s: %s", user.id, str(e))
        return ""
