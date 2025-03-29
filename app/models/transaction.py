import datetime
from app import db


class Transaction(db.Model):
    """
    Represents a financial transaction in the system.

    Attributes:
        id (int): Primary key for the transaction.
        amount (float): The monetary value of the transaction.
        description (str): Optional description of the transaction.
        timestamp (datetime): The date and time of the transaction. Defaults to the current UTC time.
        user_id (int): Foreign key referencing the user associated with the transaction.
        category_id (int): Foreign key referencing the category of the transaction.
        account_id (int): Foreign key referencing the account type of the transaction.
        is_transfer (bool): Indicates if the transaction is a transfer. Defaults to False.
    """
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)  # Transaction amount must be provided.
    description = db.Column(db.String(255))  # Optional description for the transaction.
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc))  # Default to UTC time.
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)  # Associated user ID.
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)  # Associated category ID.
    account_id = db.Column(db.Integer, db.ForeignKey("account_types.id"), nullable=False)  # Associated account type ID.
    is_transfer = db.Column(db.Boolean, default=False)  # Indicates if the transaction is a transfer.

    # Relationships
    category = db.relationship("Category", backref="transactions")  # Relationship to Category model.
    account = db.relationship("AccountType", backref="transactions")  # Relationship to AccountType model.
