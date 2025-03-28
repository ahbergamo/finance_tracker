from app import db


class ImportRule(db.Model):
    """
    Represents an import rule in the database.

    Attributes:
        id (int): Primary key for the import rule.
        account_type (str): Type of account associated with the rule.
        field_to_match (str): Field name to match against.
        match_pattern (str): Pattern to match in the specified field.
        is_transfer (bool): Indicates if the rule is for a transfer.
        override_category_id (int): Foreign key referencing the Category to override.
        family_id (int): Foreign key referencing the associated family.
    """
    __tablename__ = 'import_rules'

    id = db.Column(db.Integer, primary_key=True)
    account_type = db.Column(db.String(64), nullable=True)
    field_to_match = db.Column(db.String(32), nullable=False)
    match_pattern = db.Column(db.String(256), nullable=False)
    is_transfer = db.Column(db.Boolean, default=False)
    override_category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=True)
    family_id = db.Column(db.Integer, db.ForeignKey("family.id"), nullable=False)

    # Relationship to Category
    override_category_obj = db.relationship("Category", foreign_keys=[override_category_id])

    def __repr__(self):
        return f"<ImportRule {self.field_to_match} contains '{self.match_pattern}' (Family ID: {self.family_id})>"

    @property
    def override_category_display(self):
        """
        Returns the name of the override category if set, or an empty string.
        """
        if self.override_category_obj:
            return self.override_category_obj.name
        return ""
