from app import db


# Many-to-Many Association Table
# This table establishes a many-to-many relationship between budgets and categories.
budget_category_association = db.Table(
    "budget_category_association",
    db.Column(
        "budget_id",
        db.Integer,
        db.ForeignKey("budget.id", ondelete="CASCADE"),
        primary_key=True
    ),
    db.Column(
        "category_id",
        db.Integer,
        db.ForeignKey("category.id", ondelete="CASCADE"),
        primary_key=True
    )
)


class Budget(db.Model):
    """
    Represents a budget entity in the database.

    Attributes:
        id (int): Primary key for the budget.
        name (str): Name of the budget.
        amount (float): Total amount allocated for the budget.
        start_date (date): Start date of the budget period.
        end_date (date): End date of the budget period.
        user_id (int): Foreign key referencing the user who owns the budget.
        categories (relationship): Many-to-many relationship with the Category model.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Name of the budget
    amount = db.Column(db.Float, nullable=False)  # Allocated budget amount
    start_date = db.Column(db.Date)  # Start date of the budget
    end_date = db.Column(db.Date)  # End date of the budget
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )  # Reference to the user who owns the budget

    # Many-to-many relationship to Category
    # This relationship links budgets to categories using the association table.
    categories = db.relationship(
        "Category",
        secondary=budget_category_association,
        back_populates="budgets",  # Explicit back reference in Category
        lazy="subquery"  # Improves performance when loading related categories
    )
