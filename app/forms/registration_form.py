from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo


class RegistrationForm(FlaskForm):
    """
    A Flask-WTF form for user registration.

    Fields:
        username: The username of the user (required).
        email: The email address of the user (required, must be a valid email).
        family_name: The family name of the user (required).
        password: The password for the user account (required).
        confirm_password: Confirmation of the password (must match the password).
        submit: Submit button for the form.
    """
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    family_name = StringField("Family Name", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Register")
