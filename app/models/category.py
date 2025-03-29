from app import db
from app.models.budget import budget_category_association


class Category(db.Model):
    """
    Represents a category in the database.

    Attributes:
        id (int): The primary key of the category.
        name (str): The name of the category.
        family_id (int): Foreign key referencing the associated family.
        family (Family): Relationship to the Family model.
        budgets (list[Budget]): Relationship to the Budget model via a many-to-many association.
    """
    __tablename__ = "category"

    id = db.Column(db.Integer, primary_key=True)  # Primary key
    name = db.Column(db.String(100), nullable=False)  # Name of the category
    family_id = db.Column(db.Integer, db.ForeignKey("family.id"), nullable=False)  # Foreign key to Family

    # Relationship to Family (optional)
    family = db.relationship("Family", backref="categories")  # Establishes a one-to-many relationship with Family

    # Relationship to Budget
    budgets = db.relationship(
        "Budget",
        secondary=budget_category_association,  # Many-to-many association table
        back_populates="categories"  # Bidirectional relationship with Budget
    )

    # Ensures that the combination of name and family_id is unique
    __table_args__ = (
        db.UniqueConstraint('name', 'family_id', name='_category_family_uc'),
    )

    def __repr__(self):
        """
        Returns a string representation of the Category instance.

        Returns:
            str: A string in the format "<Category {name} (Family ID: {family_id})>".
        """
        return f"<Category {self.name} (Family ID: {self.family_id})>"
