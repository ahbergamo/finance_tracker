from flask_wtf import FlaskForm
from wtforms import DateField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional
from app.forms.fields import MoneyField


class BalanceHistoryForm(FlaskForm):
    """
    Form for adding a balance history entry to a retirement or brokerage account.
    """
    as_of_date = DateField('As of Date', validators=[DataRequired()])
    balance = MoneyField('Balance', places=2, validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Add Balance')
