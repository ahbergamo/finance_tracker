from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, SelectField, DecimalField
from wtforms.validators import DataRequired, Optional


class AccountTypeForm(FlaskForm):
    """
    A form for defining accounts and mapping CSV columns to specific fields.

    Attributes:
        name (StringField): The name of the account.
        account_type (SelectField): Type of account (checking, savings, credit_card, retirement, brokerage).
        retirement_type (SelectField): Subtype for retirement accounts.
        initial_balance (DecimalField): Starting balance for the account.
        category_field (StringField): The CSV column that maps to the category.
        date_field (StringField): The CSV column that maps to the date.
        amount_field (StringField): The CSV column that maps to the amount.
        description_field (StringField): The CSV column that maps to the description.
        positive_expense (BooleanField): Checkbox to indicate whether expenses are positive values.
        submit (SubmitField): Button to submit the form.
    """
    name = StringField('Account Name', validators=[DataRequired()])

    account_type = SelectField(
        'Account Type',
        choices=[
            ('checking', 'Checking'),
            ('savings', 'Savings'),
            ('credit_card', 'Credit Card'),
            ('retirement', 'Retirement'),
            ('brokerage', 'Brokerage')
        ],
        default='checking'
    )

    retirement_type = SelectField(
        'Retirement Type',
        choices=[
            ('', '-- Select Type --'),
            ('traditional_401k', 'Traditional 401(k)'),
            ('roth_401k', 'Roth 401(k)'),
            ('traditional_ira', 'Traditional IRA'),
            ('roth_ira', 'Roth IRA'),
            ('sep_ira', 'SEP IRA'),
            ('403b', '403(b)')
        ],
        validators=[Optional()]
    )

    initial_balance = DecimalField(
        'Initial Balance',
        places=2,
        default=0,
        validators=[Optional()]
    )

    # CSV field mappings (optional for retirement/brokerage accounts)
    category_field = StringField('CSV Column for Category', validators=[Optional()])
    date_field = StringField('CSV Column for Date', validators=[Optional()])
    amount_field = StringField('CSV Column for Amount', validators=[Optional()])
    description_field = StringField('CSV Column for Description', validators=[Optional()])
    positive_expense = BooleanField('Positive Expense')

    submit = SubmitField('Save')
