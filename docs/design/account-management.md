# Account Management

**Status:** 🔵 In Review
**Created:** 2025-12-20
**Updated:** 2025-12-21
**Author:** FRacker Team

## Overview

Extend the existing `AccountType` model (renamed to `Account`) to support different account types and balance tracking. This enables retirement and brokerage accounts to be tracked separately from transaction-based accounts.

### Problem Statement

Currently, FRacker tracks all accounts the same way - by summing transactions. This doesn't work for:

- **Retirement accounts (401k, IRA, etc.)** - Balances change due to market gains/losses, not just transactions
- **Brokerage accounts** - Same issue, balance comes from statements

Users need to record actual account balances from their statements, not create fake transactions for market changes.

### Goals

- Add account type classification (checking, savings, credit_card, retirement, brokerage)
- Add retirement subtype for tax planning (traditional_401k, roth_401k, etc.)
- Add initial balance field for seeding account history
- Add balance history tracking for retirement/brokerage accounts
- Keep transaction-based balance calculation for checking/savings/credit
- Maintain backward compatibility

### Non-Goals

- Automated bank connections
- Individual investment holdings tracking
- Multi-currency support

## Solution

### 1. Rename AccountType to Account

Rename the existing model and table:
- Model: `AccountType` → `Account`
- Table: `account_types` → `accounts`
- Update all references throughout codebase

### 2. Add Fields to Account Model

```python
class Account(db.Model):
    __tablename__ = 'accounts'

    # Existing fields (unchanged)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    category_field = db.Column(db.String(64), nullable=True)  # Make nullable for retirement
    date_field = db.Column(db.String(64), nullable=True)
    amount_field = db.Column(db.String(64), nullable=True)
    description_field = db.Column(db.String(128), nullable=True)
    family_id = db.Column(db.Integer, db.ForeignKey("family.id"), nullable=False)
    positive_expense = db.Column(db.Boolean, default=False)

    # New fields
    account_type = db.Column(
        db.Enum('checking', 'savings', 'credit_card', 'retirement', 'brokerage'),
        default='checking',
        nullable=False
    )
    retirement_type = db.Column(
        db.Enum('traditional_401k', 'roth_401k', 'traditional_ira', 'roth_ira', 'sep_ira', '403b'),
        nullable=True  # Only set when account_type='retirement'
    )
    initial_balance = db.Column(db.Numeric(15, 2), default=0)
```

### 3. Add AccountBalanceHistory Table

```python
class AccountBalanceHistory(db.Model):
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
    )
```

### 4. Balance Calculation Logic

```python
def get_current_balance(account):
    """Calculate current balance based on account type."""
    if account.account_type in ('checking', 'savings', 'credit_card'):
        # Transaction-based: initial_balance + sum(transactions)
        transaction_sum = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.account_id == account.id
        ).scalar() or 0
        return account.initial_balance + transaction_sum
    else:
        # Balance-based (retirement, brokerage): latest balance history entry
        latest = AccountBalanceHistory.query.filter_by(
            account_id=account.id
        ).order_by(AccountBalanceHistory.as_of_date.desc()).first()
        return latest.balance if latest else account.initial_balance
```

## Database Migration

### Migration 1: Rename table and add new fields

```python
def upgrade():
    # Rename table
    op.rename_table('account_types', 'accounts')

    # Add new columns
    op.add_column('accounts', sa.Column('account_type',
        sa.Enum('checking', 'savings', 'credit_card', 'retirement', 'brokerage'),
        nullable=False, server_default='checking'))
    op.add_column('accounts', sa.Column('retirement_type',
        sa.Enum('traditional_401k', 'roth_401k', 'traditional_ira', 'roth_ira', 'sep_ira', '403b'),
        nullable=True))
    op.add_column('accounts', sa.Column('initial_balance',
        sa.Numeric(15, 2), nullable=False, server_default='0'))

    # Make CSV fields nullable (for retirement/brokerage accounts)
    op.alter_column('accounts', 'category_field', nullable=True)
    op.alter_column('accounts', 'date_field', nullable=True)
    op.alter_column('accounts', 'amount_field', nullable=True)
    op.alter_column('accounts', 'description_field', nullable=True)

    # Auto-detect account types from names
    connection = op.get_bind()
    connection.execute(text("""
        UPDATE accounts SET account_type = 'retirement', retirement_type = 'traditional_401k'
        WHERE LOWER(name) LIKE '%401k%' AND LOWER(name) NOT LIKE '%roth%'
    """))
    connection.execute(text("""
        UPDATE accounts SET account_type = 'retirement', retirement_type = 'roth_401k'
        WHERE LOWER(name) LIKE '%roth%' AND LOWER(name) LIKE '%401k%'
    """))
    # ... similar for IRA, 403b, etc.
```

### Migration 2: Create balance history table

```python
def upgrade():
    op.create_table('account_balance_history',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('account_id', sa.Integer, sa.ForeignKey('accounts.id'), nullable=False),
        sa.Column('balance', sa.Numeric(15, 2), nullable=False),
        sa.Column('as_of_date', sa.Date, nullable=False),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow),
        sa.UniqueConstraint('account_id', 'as_of_date', name='unique_account_date'),
        sa.Index('idx_account_date', 'account_id', 'as_of_date')
    )
```

## UI Changes

### Account List Page (`/accounts`)

**Current columns:**
| Name | CSV Category | CSV Date | CSV Amount | CSV Description | Positive Expense? | Actions |

**New columns:**
| Name | Type | Balance | Actions |

- **Type**: Shows account_type (and retirement_type if applicable)
- **Balance**: Calculated based on account type
- **Actions**: [Edit] [Delete] + [Update Balance] for retirement/brokerage

### Add/Edit Account Form

**Add new fields:**
- Account Type (dropdown: Checking, Savings, Credit Card, Retirement, Brokerage)
- Retirement Type (dropdown, only shown when Account Type = Retirement)
- Initial Balance (currency input)

**CSV fields** remain but are optional for retirement/brokerage.

### Balance History View (for retirement/brokerage)

When viewing a retirement/brokerage account:

```
401k - Vanguard
Current Balance: $45,000.00 (as of Dec 15, 2025)

[+ Add Balance Entry]

Balance History:
Date         Balance      Change       Notes                 Actions
2025-12-15   $45,000.00   +$1,200.00   Q4 statement         [Edit] [Delete]
2025-09-15   $43,800.00   +$2,300.00   Q3 statement         [Edit] [Delete]
2025-06-15   $41,500.00   +$1,500.00   Q2 statement         [Edit] [Delete]
```

### Transaction Page Filter

Update account dropdown to only show transaction-based accounts:
- Checking
- Savings
- Credit Card

Retirement and brokerage accounts are excluded (they don't have transactions).

## File Changes Required

### Models
- Rename `app/models/account_type.py` → `app/models/account.py`
- Update model class name
- Add new fields
- Create `app/models/account_balance_history.py`

### Routes
- Rename `app/routes/account_types.py` → `app/routes/accounts.py`
- Update blueprint name
- Add balance history CRUD routes

### Templates
- Rename `app/templates/account_types/` → `app/templates/accounts/`
- Update index.html with new columns
- Update add/edit forms with new fields
- Add balance history template

### Services
- Create `app/services/account_service.py` with balance calculation
- Create `app/services/balance_history_service.py`

### Other Updates
- Update `app/__init__.py` blueprint registration
- Update `base.html` navigation
- Update transaction routes to filter accounts
- Update retirement report to use balance history

## Testing

- Model tests for Account with new fields
- Model tests for AccountBalanceHistory
- Balance calculation tests (transaction-based vs balance-based)
- Migration tests (existing accounts get correct types)
- Route tests for account CRUD
- Route tests for balance history CRUD
- Family scoping tests

## Future Considerations

### AI Analysis Integration

The clean `account_type` field enables future AI analysis:
- Spending patterns on checking/credit accounts
- Savings rate calculations
- Retirement contribution tracking
- Net worth projections
- Anomaly detection
- Personalized financial insights

### Asset Tracking

Same pattern extends to assets:
- Add `account_type` values: `asset_real_estate`, `asset_vehicle`, `asset_other`
- Use `AccountBalanceHistory` for property valuations
- Net worth = sum of all account balances

---

## Implementation Plan

### Phase 1: Model & Migration
- [ ] Create migration to rename table and add fields
- [ ] Create AccountBalanceHistory model
- [ ] Update Account model
- [ ] Update all model references

### Phase 2: Routes & Services
- [ ] Create account service with balance calculation
- [ ] Create balance history service
- [ ] Update account routes
- [ ] Add balance history routes

### Phase 3: UI
- [ ] Update account templates
- [ ] Add balance history view
- [ ] Update transaction page filter
- [ ] Update navigation

### Phase 4: Reports
- [ ] Update retirement report to use balance history
- [ ] Add balance trend charts

### Phase 5: Testing
- [ ] Add tests for all new functionality
- [ ] Verify migration works with existing data
