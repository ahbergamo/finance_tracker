from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length


# Define a form for updating user profile information
class ProfileForm(FlaskForm):
    """
    A form for updating user profile information, including username, email, and family name.
    """
    # Field for the username, required
    username = StringField("Username", validators=[DataRequired()])

    # Field for the email, required and must be a valid email address
    email = StringField("Email", validators=[DataRequired(), Email()])

    # Optional field for the family name with a maximum length of 50 characters
    family_name = StringField("Family Name", validators=[Length(max=50)])  # Optional

    # Submit button for the form
    submit = SubmitField("Update Profile")
