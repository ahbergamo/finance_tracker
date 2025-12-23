# Account Management

**Status:** Done
**Created:** 2025-12-20
**Updated:** 2025-12-23
**Author:** FRacker Team

## Overview

Extended the existing `AccountType` model (renamed to `Account`) to support different account types and balance tracking. This enables retirement, brokerage, and asset accounts to be tracked separately from transaction-based accounts.

### Problem Statement

Previously, FRacker tracked all accounts the same way - by summing transactions. This doesn't work for:

- **Retirement accounts (401k, IRA, etc.)** - Balances change due to market gains/losses, not just transactions
- **Brokerage accounts** - Same issue, balance comes from statements
- **Real estate, vehicles, other assets** - Value changes over time, no transactions

Users need to record actual account balances from their statements, not create fake transactions for market changes.

### Goals

- Add account type classification (checking, savings, credit_card, retirement, brokerage, real_estate, vehicle, other_asset, loan)
- Add retirement subtype for tax planning (traditional_401k, roth_401k, etc.)
- Add initial balance field for seeding account history
- Add balance history tracking for non-transaction accounts
- Keep transaction-based balance calculation for checking/savings/credit
- Net worth report showing all assets and liabilities

### Non-Goals

- Automated bank connections
- Individual investment holdings tracking
- Multi-currency support

## Implementation (Completed)

### Account Model

```python
class Account(db.Model):
    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    category_field = db.Column(db.String(64), nullable=True)
    date_field = db.Column(db.String(64), nullable=True)
    amount_field = db.Column(db.String(64), nullable=True)
    description_field = db.Column(db.String(128), nullable=True)
    family_id = db.Column(db.Integer, db.ForeignKey("family.id"), nullable=False)
    positive_expense = db.Column(db.Boolean, default=False)

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
```

### AccountBalanceHistory Model

```python
class AccountBalanceHistory(db.Model):
    __tablename__ = 'account_balance_history'

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    balance = db.Column(db.Numeric(15, 2), nullable=False)
    as_of_date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('account_id', 'as_of_date', name='unique_account_date'),
    )
```

### Balance Calculation Logic

Located in `app/services/reports/net_worth.py`:

- **Transaction-based accounts** (checking, savings, credit_card): `initial_balance + sum(transactions)`
- **Balance-history accounts** (retirement, brokerage, real_estate, vehicle, other_asset, loan): Latest balance history entry, or initial_balance if none

### Account Types

| Type | Balance Method | Asset/Liability |
|------|---------------|-----------------|
| checking | Transactions | Asset (or liability if negative) |
| savings | Transactions | Asset |
| credit_card | Transactions | Liability if negative, asset if positive |
| retirement | Balance History | Asset |
| brokerage | Balance History | Asset |
| real_estate | Balance History | Asset |
| vehicle | Balance History | Asset |
| other_asset | Balance History | Asset |
| loan | Balance History | Always Liability |

## UI Implementation

### Account List Page (`/account_types`)

Shows all accounts with:
- Name
- Type (plain text with retirement subtype if applicable)
- Current Balance (calculated)
- Actions: Balance History (for non-transaction accounts), Edit, Delete

### Add/Edit Account Form

- Account Type dropdown with "-- Select Type --" placeholder
- Retirement Type dropdown (only visible when Account Type = Retirement)
- Initial Balance field (accepts comma-formatted input like "$12,234.44")
- Pre-defined Account dropdown (only visible for checking/savings/credit_card)
- CSV field mappings (hidden for balance-history account types)

### Balance History View (`/accounts/<id>/balances`)

For retirement, brokerage, real_estate, vehicle, other_asset, and loan accounts:
- Add new balance entry form (date, balance, notes)
- List of historical balances with delete option
- Updates to same date overwrite existing entry

### Net Worth Report (`/reports/net_worth`)

- Summary cards: Total Assets, Total Liabilities, Net Worth
- 12-month chart showing net worth, assets, and liabilities over time
- Account breakdown by type (Assets column, Liabilities column)

## Files Changed

### Models
- `app/models/account.py` - Extended with new fields and account types
- `app/models/account_balance_history.py` - New model for balance snapshots

### Forms
- `app/forms/account_type_form.py` - Added account_type, retirement_type, initial_balance
- `app/forms/balance_history_form.py` - New form for adding balance entries
- `app/forms/fields.py` - New MoneyField for comma-formatted currency input

### Routes
- `app/routes/account_types.py` - Updated to show balances, handle new account types
- `app/routes/balance_history.py` - New routes for balance history CRUD
- `app/routes/reports/net_worth.py` - New route for net worth report

### Services
- `app/services/reports/net_worth.py` - Balance calculation, net worth summary, historical data

### Templates
- `app/templates/account_types/index.html` - Balance column, type display, balance history button
- `app/templates/account_types/add_account_type.html` - Dynamic form with JS for showing/hiding fields
- `app/templates/balance_history/index.html` - Balance history view
- `app/templates/reports/net_worth.html` - Net worth report with Chart.js

### Tests
- `tests/models/test_account_balance_history.py` - Model tests
- `tests/routes/test_balance_history.py` - Route tests
- `tests/routes/test_net_worth.py` - Net worth route tests
- `tests/services/reports/test_net_worth.py` - 17 tests for balance calculation math

## Testing

168 tests passing with the following coverage for new code:
- Balance calculation tests verify transaction-based vs history-based logic
- Net worth summary tests verify asset/liability classification
- Tests for real_estate, vehicle, loan account types
