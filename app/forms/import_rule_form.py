from flask_wtf import FlaskForm
from flask import current_app
from wtforms import StringField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional


class ImportRuleForm(FlaskForm):
    """
    A form for creating or editing import rules.

    Attributes:
        account_type (StringField): Optional field for specifying the account type.
        field_to_match (StringField): Required field to specify the field to match (e.g., "description" or "category").
        match_pattern (StringField): Required field for the pattern to match.
        is_transfer (BooleanField): Checkbox to mark the rule as a transfer.
        override_category (SelectField): Dropdown to select or override the category.
        submit (SubmitField): Button to submit the form.
    """

    account_type = StringField(
        'Account Type (optional)',
        validators=[Optional()]
    )
    field_to_match = StringField(
        'Field to Match',
        validators=[DataRequired()]
    )
    match_pattern = StringField(
        'Match Pattern',
        validators=[DataRequired()]
    )
    is_transfer = BooleanField(
        'Mark as Transfer?'
    )
    override_category = SelectField(
        'Override Category (optional)',
        validators=[Optional()],
        choices=[]
    )
    submit = SubmitField('Save')

    def __init__(self, family_id: int, *args, **kwargs):
        """
        Initialize the form and populate the override_category choices.

        Args:
            family_id (int): The ID of the family whose categories should be loaded.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        The override_category field is populated with:
        - An empty option.
        - Categories belonging to the given family, sorted alphabetically.
        - An "Other" option for entering a new category.
        """
        super(ImportRuleForm, self).__init__(*args, **kwargs)
        from app.models.category import Category
        try:
            categories = Category.query.filter_by(family_id=family_id).order_by(Category.name.asc()).all()
        except Exception as e:
            # Log the error and set categories to an empty list if the query fails
            categories = []
            current_app.logger.error("Error fetching categories for family_id %s: %s", family_id, e)

        self.override_category.choices = [('', 'Select a Category (optional)')]
        self.override_category.choices += [(str(c.id), c.name) for c in categories]
        self.override_category.choices += [('other', 'Other (enter new)')]
