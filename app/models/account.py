from app import db


class Account(db.Model):
    """
    Represents an account in the system.

    Accounts can be transaction-based (checking, savings, credit_card) where balance
    is calculated from transactions, or balance-based (retirement, brokerage) where
    balance comes from periodic snapshots.

    Attributes:
        id (int): Primary key for the account.
        name (str): Name of the account.
        category_field (str): CSV column for category (nullable for balance-based accounts).
        date_field (str): CSV column for date (nullable for balance-based accounts).
        amount_field (str): CSV column for amount (nullable for balance-based accounts).
        description_field (str): CSV column for description (nullable for balance-based accounts).
        family_id (int): Foreign key referencing the associated family.
        positive_expense (bool): Indicates if expenses are positive values in CSV.
        account_type (str): Type of account (checking, savings, credit_card, retirement, brokerage).
        retirement_type (str): Subtype for retirement accounts (traditional_401k, roth_401k, etc.).
        initial_balance (Decimal): Starting balance for the account.
    """
    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    category_field = db.Column(db.String(64), nullable=True)
    date_field = db.Column(db.String(64), nullable=True)
    amount_field = db.Column(db.String(64), nullable=True)
    description_field = db.Column(db.String(128), nullable=True)
    family_id = db.Column(db.Integer, db.ForeignKey("family.id"), nullable=False)
    positive_expense = db.Column(db.Boolean, default=False)

    # New fields for account management
    account_type = db.Column(
        db.Enum('checking', 'savings', 'credit_card', 'retirement', 'brokerage',
                'real_estate', 'vehicle', 'other_asset', 'loan',
                name='account_type_enum'),
        default='checking',
        nullable=False
    )
    retirement_type = db.Column(
        db.Enum('traditional_401k', 'roth_401k', 'traditional_ira', 'roth_ira', 'sep_ira', '403b',
                name='retirement_type_enum'),
        nullable=True
    )
    initial_balance = db.Column(db.Numeric(15, 2), default=0, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('name', 'family_id', name='_account_family_uc'),
    )

    def __repr__(self):
        """
        Returns a string representation of the Account instance.

        Returns:
            str: A string in the format '<Account {name} (Family ID: {family_id})>'.
        """
        return f'<Account {self.name} (Family ID: {self.family_id})>'

    def is_transaction_based(self):
        """Check if this account uses transaction-based balance calculation."""
        return self.account_type in ('checking', 'savings', 'credit_card')

    def is_balance_based(self):
        """Check if this account uses balance snapshot tracking."""
        return self.account_type in ('retirement', 'brokerage', 'real_estate', 'vehicle', 'other_asset', 'loan')


# Keep AccountType as an alias for backward compatibility during migration
AccountType = Account
