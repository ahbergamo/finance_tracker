from datetime import date
from decimal import Decimal
from app import db


# Account types that support transactions (CSV import, manual entry)
TRANSACTION_ACCOUNT_TYPES = ('checking', 'savings', 'credit_card')

# Account types that use balance history instead of transactions
BALANCE_HISTORY_ACCOUNT_TYPES = ('retirement', 'brokerage', 'real_estate', 'vehicle', 'other_asset', 'loan')

# Default assumptions for pension present value calculation
PENSION_DISCOUNT_RATE = Decimal('0.04')  # 4% annual discount rate
PENSION_YEARS_RECEIVING = 20  # Assume 20 years of payments


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
        db.Enum('traditional_401k', 'roth_401k', 'traditional_ira', 'roth_ira', 'sep_ira', '403b', 'pension',
                name='retirement_type_enum'),
        nullable=True
    )
    initial_balance = db.Column(db.Numeric(15, 2), default=0, nullable=False)

    # Pension-specific fields (only used when retirement_type = 'pension')
    pension_monthly_benefit = db.Column(db.Numeric(10, 2), nullable=True)
    pension_start_date = db.Column(db.Date, nullable=True)

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

    def is_pension(self):
        """Check if this is a pension account."""
        return self.account_type == 'retirement' and self.retirement_type == 'pension'

    def get_pension_present_value(self, discount_rate=None, years_receiving=None):
        """
        Calculate the present value of a pension.

        Uses a simple discounted cash flow model:
        - Total future value = monthly_benefit * 12 * years_receiving
        - Present value = future_value / (1 + discount_rate)^years_until_start

        Args:
            discount_rate: Annual discount rate (default 4%)
            years_receiving: Expected years of pension payments (default 20)

        Returns:
            Decimal: Estimated present value, or 0 if not a pension or missing data
        """
        if not self.is_pension():
            return Decimal('0')

        if not self.pension_monthly_benefit or not self.pension_start_date:
            return Decimal('0')

        if discount_rate is None:
            discount_rate = PENSION_DISCOUNT_RATE
        if years_receiving is None:
            years_receiving = PENSION_YEARS_RECEIVING

        # Calculate years until pension starts
        today = date.today()
        if self.pension_start_date <= today:
            # Pension has already started - just return remaining value
            years_until_start = 0
        else:
            days_until_start = (self.pension_start_date - today).days
            years_until_start = Decimal(days_until_start) / Decimal('365')

        # Calculate future value (total expected payments)
        annual_benefit = self.pension_monthly_benefit * 12
        future_value = annual_benefit * years_receiving

        # Discount to present value
        if years_until_start > 0:
            discount_factor = (1 + discount_rate) ** years_until_start
            present_value = future_value / discount_factor
        else:
            present_value = future_value

        return present_value.quantize(Decimal('0.01'))


# Keep AccountType as an alias for backward compatibility during migration
AccountType = Account
