from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectMultipleField, DateField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional
from app.models.category import Category


def populate_category_choices(family_id):
    """
    Helper function to populate category choices based on the family ID.

    :param family_id: ID of the family to filter categories
    :return: List of tuples containing category IDs and names
    """
    try:
        return [
            (c.id, c.name) for c in Category.query
            .filter_by(family_id=family_id)
            .order_by(Category.name.asc())
            .all()
        ]
    except Exception as e:
        # Log the error and return an empty list if the query fails
        print(f"Error fetching categories for family_id {family_id}: {e}")
        return []


class EditBudgetForm(FlaskForm):
    # Form fields for editing a budget
    name = StringField("Budget Name", validators=[DataRequired()])
    amount = DecimalField("Amount", validators=[DataRequired(), NumberRange(min=0)], places=2)
    start_date = DateField("Start Date", validators=[Optional()])
    end_date = DateField("End Date", validators=[Optional()])
    # Use coerce=int to convert selected values to integers
    category_ids = SelectMultipleField("Categories", coerce=int)
    submit = SubmitField("Update Budget")

    def __init__(self, family_id, *args, **kwargs):
        """
        Initialize the form and set the category choices to only those categories
        that belong to the given family.

        :param family_id: ID of the family to filter categories
        :param args: Additional positional arguments
        :param kwargs: Additional keyword arguments
        """
        super(EditBudgetForm, self).__init__(*args, **kwargs)
        # Populate category choices using the helper function
        self.category_ids.choices = populate_category_choices(family_id)

    def validate_category_ids(self, field):
        """
        Ensure category_ids is never None and properly handles multi-select inputs.

        :param field: The field to validate
        """
        if field.data is None:
            field.data = []
        elif not isinstance(field.data, list):
            field.data = [field.data]  # Ensure data is always a list


class AddBudgetForm(FlaskForm):
    # Form fields for adding a new budget
    name = StringField("Budget Name", validators=[DataRequired()])
    amount = DecimalField("Amount", validators=[DataRequired(), NumberRange(min=0)], places=2)
    start_date = DateField("Start Date", validators=[Optional()])
    end_date = DateField("End Date", validators=[Optional()])
    # Use coerce=int for proper type conversion
    category_ids = SelectMultipleField("Categories", coerce=int)
    submit = SubmitField("Add Budget")

    def __init__(self, family_id, *args, **kwargs):
        """
        Initialize the form and set the category choices to only those categories
        that belong to the given family. Also ensure category_ids is initialized to an empty list if needed.

        :param family_id: ID of the family to filter categories
        :param args: Additional positional arguments
        :param kwargs: Additional keyword arguments
        """
        super(AddBudgetForm, self).__init__(*args, **kwargs)
        # Populate category choices using the helper function
        self.category_ids.choices = populate_category_choices(family_id)
        # Ensure category_ids is not None
        EditBudgetForm.validate_category_ids(self, self.category_ids)
