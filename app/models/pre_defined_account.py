from app import db


class PreDefinedAccount(db.Model):
    """
    Represents a predefined account in the system.

    Attributes:
        id (int): Primary key for the predefined account.
        name (str): Unique name of the predefined account.
        category_field (str): Category associated with the account.
        date_field (str): Date field for the account.
        amount_field (str): Amount field for the account.
        description_field (str, optional): Description of the account.
        positive_expense (bool): Indicates if the account represents a positive expense.
    """
    __tablename__ = 'pre_defined_accounts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    category_field = db.Column(db.String(64), nullable=False)
    date_field = db.Column(db.String(64), nullable=False)
    amount_field = db.Column(db.String(64), nullable=False)
    description_field = db.Column(db.String(255), nullable=True)
    positive_expense = db.Column(db.Boolean, default=False)

    def __repr__(self):
        """
        Returns a string representation of the PreDefinedAccount instance.

        Returns:
            str: String representation of the account.
        """
        return f'<PreDefinedAccount {self.name}>'
