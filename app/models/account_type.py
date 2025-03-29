from app import db


class AccountType(db.Model):
    """
    Represents an account type in the system.

    Attributes:
        id (int): Primary key for the account type.
        name (str): Name of the account type.
        category_field (str): Category field associated with the account type.
        date_field (str): Date field associated with the account type.
        amount_field (str): Amount field associated with the account type.
        description_field (str): Description field for the account type.
        family_id (int): Foreign key referencing the associated family.
        positive_expense (bool): Indicates if the account type represents a positive expense.
    """
    __tablename__ = 'account_types'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    category_field = db.Column(db.String(64), nullable=False)
    date_field = db.Column(db.String(64), nullable=False)
    amount_field = db.Column(db.String(64), nullable=False)
    description_field = db.Column(db.String(128), nullable=False)
    family_id = db.Column(db.Integer, db.ForeignKey("family.id"), nullable=False)
    positive_expense = db.Column(db.Boolean, default=False)

    __table_args__ = (
        db.UniqueConstraint('name', 'family_id', name='_accounttype_family_uc'),
    )

    def __repr__(self):
        """
        Returns a string representation of the AccountType instance.

        Returns:
            str: A string in the format '<AccountType {name} (Family ID: {family_id})>'.
        """
        return f'<AccountType {self.name} (Family ID: {self.family_id})>'
