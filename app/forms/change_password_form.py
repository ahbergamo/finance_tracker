from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError
import re


def strong_password(form, field):
    """
    Custom validator to ensure the password contains at least one uppercase letter,
    one lowercase letter, one digit, and one special character.
    """
    password = field.data
    if not re.search(r'[A-Z]', password):
        raise ValidationError("Password must contain at least one uppercase letter.")
    if not re.search(r'[a-z]', password):
        raise ValidationError("Password must contain at least one lowercase letter.")
    if not re.search(r'\d', password):
        raise ValidationError("Password must contain at least one digit.")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError("Password must contain at least one special character.")


class ChangePasswordForm(FlaskForm):
    """
    A form for handling password change requests.

    Attributes:
        current_password (PasswordField): Field for entering the current password.
        new_password (PasswordField): Field for entering the new password.
        confirm_new_password (PasswordField): Field for confirming the new password.
        submit (SubmitField): Submit button for the form.
    """
    current_password = PasswordField(
        "Current Password",
        validators=[DataRequired()]
    )
    new_password = PasswordField(
        "New Password",
        validators=[DataRequired(), Length(min=6)]
        # If you want to enforce a strong password, use the following line instead
        # validators=[DataRequired(), Length(min=6), strong_password]
    )
    confirm_new_password = PasswordField(
        "Confirm New Password",
        validators=[
            DataRequired(),
            EqualTo("new_password", message="Passwords must match")
        ]
    )
    submit = SubmitField("Change Password")
