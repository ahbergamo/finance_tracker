from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


# Define a login form for user authentication.
# This form includes fields for username, password, a "remember me" checkbox, and a submit button.
class LoginForm(FlaskForm):
    # Field for entering the username. This field is required.
    username = StringField("Username", validators=[DataRequired()])
    # Field for entering the password. This field is required.
    password = PasswordField("Password", validators=[DataRequired()])
    # Checkbox to allow users to choose whether to remember their session.
    remember_me = BooleanField("Remember Me")
    # Submit button to submit the form.
    submit = SubmitField("Login")
