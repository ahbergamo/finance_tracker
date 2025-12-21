from datetime import datetime
from app import db


class AccountBalanceHistory(db.Model):
    """
    Tracks balance snapshots for balance-based accounts (retirement, brokerage).

    Users record their account balance periodically (e.g., from quarterly statements).
    The most recent entry represents the current balance.

    Attributes:
        id (int): Primary key.
        account_id (int): Foreign key to the account.
        balance (Decimal): The account balance as of the date.
        as_of_date (date): The date this balance was recorded for.
        notes (str): Optional notes (e.g., "Q4 2025 statement").
        created_at (datetime): When this record was created.
    """
    __tablename__ = 'account_balance_history'

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    balance = db.Column(db.Numeric(15, 2), nullable=False)
    as_of_date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    account = db.relationship('Account', backref='balance_history')

    __table_args__ = (
        db.UniqueConstraint('account_id', 'as_of_date', name='unique_account_date'),
        db.Index('idx_account_date', 'account_id', 'as_of_date'),
    )

    def __repr__(self):
        return f'<AccountBalanceHistory {self.account_id} ${self.balance} @ {self.as_of_date}>'
