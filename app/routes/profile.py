from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.forms.profile_form import ProfileForm
from app.services.profile import (
    update_user_profile,
    get_family_name_for_user
)


profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    """
    Route to edit the user's profile. Handles both GET and POST requests.
    """
    form = ProfileForm(obj=current_user)

    if form.validate_on_submit():
        success = update_user_profile(
            user=current_user,
            username=form.username.data,
            email=form.email.data,
            family_name=form.family_name.data
        )
        if success:
            flash("Profile updated successfully.", "success")
        else:
            flash("An error occurred while updating your profile. Please try again.", "danger")

        return redirect(url_for("profile.edit_profile"))

    # Pre-populate the family name into the form
    form.family_name.data = get_family_name_for_user(current_user)
    current_app.logger.debug("Rendering profile edit form for user ID %s", current_user.id)
    return render_template("user/profile.html", form=form)
