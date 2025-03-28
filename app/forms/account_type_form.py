from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class AccountTypeForm(FlaskForm):
    """
    A form for defining account types and mapping CSV columns to specific fields.

    Attributes:
        name (StringField): The name of the account type.
        category_field (StringField): The CSV column that maps to the category.
        date_field (StringField): The CSV column that maps to the date.
        amount_field (StringField): The CSV column that maps to the amount.
        description_field (StringField): The CSV column that maps to the description.
        positive_expense (BooleanField): Checkbox to indicate whether expenses are positive values.
        submit (SubmitField): Button to submit the form.
    """
    name = StringField('Account Type Name', validators=[DataRequired()])
    category_field = StringField('CSV Column for Category', validators=[DataRequired()])
    date_field = StringField('CSV Column for Date', validators=[DataRequired()])
    amount_field = StringField('CSV Column for Amount', validators=[DataRequired()])
    description_field = StringField('CSV Column for Description', validators=[DataRequired()])
    positive_expense = BooleanField('Positive Expense')
    submit = SubmitField('Save')
