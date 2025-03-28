from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.services.auth import register_user, authenticate_user
from app.forms.login_form import LoginForm
from app.forms.registration_form import RegistrationForm
from app.forms.change_password_form import ChangePasswordForm
from app.models.family import Family
from app import db


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Handle user login requests. Validates the login form and authenticates the user.
    """
    form = LoginForm()
    if form.validate_on_submit():
        current_app.logger.info("Login attempt for user: %s", form.username.data)
        user = authenticate_user(form.username.data, form.password.data)
        if user:
            _login_user_with_remember_option(user, form.remember_me.data)
            return redirect(url_for("dashboard.dashboard"))
        else:
            current_app.logger.warning("Failed login attempt for username: %s", form.username.data)
            flash("Invalid username or password.", "danger")
    return render_template("user/login.html", form=form)


def _login_user_with_remember_option(user, remember):
    """
    Log in the user with the 'remember me' option.
    """
    current_app.logger.info("Remember me is set to: %s", remember)
    login_user(user, remember=remember)
    current_app.logger.info("User %s logged in successfully.", user.username)
    flash("Logged in successfully.", "success")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    Handle user registration requests. Validates the registration form and creates a new user.
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        current_app.logger.info("Registration attempt for user: %s", form.username.data)
        family = _get_or_create_family(form.family_name.data.strip())
        if family:
            user = _register_and_login_user(form, family)
            if user:
                return redirect(url_for("dashboard.dashboard"))
    return render_template("user/register.html", form=form)


def _get_or_create_family(family_name):
    """
    Retrieve an existing family by name or create a new one.
    """
    try:
        family = Family.query.filter_by(name=family_name).first()
        if not family:
            family = Family(name=family_name)
            db.session.add(family)
            db.session.commit()
            current_app.logger.info("Created new family: %s", family_name)
        return family
    except Exception as e:
        current_app.logger.error("Error accessing or creating family: %s", str(e))
        flash("An error occurred while processing your request. Please try again.", "danger")
        return None


def _register_and_login_user(form, family):
    """
    Register a new user and log them in.
    """
    try:
        user = register_user(form.username.data, form.email.data, form.password.data)
        if user:
            user.family_id = family.id
            db.session.commit()
            login_user(user)
            current_app.logger.info("User %s registered and logged in successfully.", user.username)
            flash("Registration successful. You are now logged in.", "success")
            return user
    except Exception as e:
        current_app.logger.error("Registration failed for user: %s. Error: %s", form.username.data, str(e))
        flash("Registration failed. Please try again.", "danger")
    return None


@auth_bp.route("/logout")
@login_required
def logout():
    """
    Handle user logout requests.
    """
    current_app.logger.info("User %s logged out.", current_user.username)
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for("auth.login"))


@auth_bp.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    """
    Handle password change requests. Validates the form and updates the user's password.
    """
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash("Incorrect current password.", "danger")
        else:
            _update_user_password(form.new_password.data)
            return redirect(url_for("auth.login"))
    return render_template("user/change_password.html", form=form)


def _update_user_password(new_password):
    """
    Update the current user's password.
    """
    try:
        current_user.set_password(new_password)
        db.session.commit()
        flash("Password updated successfully.", "success")
        current_app.logger.info("User %s changed password successfully.", current_user.username)
    except Exception as e:
        current_app.logger.error("Error updating password for user %s: %s", current_user.username, str(e))
        flash("An error occurred while updating your password. Please try again.", "danger")
