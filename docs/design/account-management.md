# Account Management System

**Status:** 🔵 In Review
**Created:** 2025-12-20
**Author:** FRacker Team

## Overview

Add a comprehensive Account Management system to FRacker, separating the concept of "accounts" (actual financial accounts like checking, savings, credit cards) from "account types" (CSV import templates). This feature enables users to track multiple accounts of the same type and provides a foundation for retirement account and asset tracking.

### Problem Statement

Currently, FRacker uses `AccountType` to serve two conflicting purposes:

1. **CSV Import Template**: Defines how to parse CSV files from different banks
2. **Account Identifier**: Transactions reference AccountType to indicate which "account" they belong to

**Limitations:**
- Cannot have multiple accounts of the same type (e.g., two Chase checking accounts)
- Confusing semantics ("account settings" vs actual accounts)
- No way to track account balances or history
- Cannot support retirement/brokerage accounts (need periodic value updates, not transactions)

### Goals

- Separate Account model from AccountType
- Support multiple accounts of the same type
- Track account balances over time
- Categorize accounts (checking, savings, credit_card, retirement, brokerage, other)
- Maintain backward compatibility with existing transactions
- Provide foundation for retirement and asset tracking features

### Non-Goals (for initial implementation)

- Automated bank connections (Plaid, etc.)
- Investment portfolio tracking (individual holdings, cost basis)
- Liability tracking (loans, mortgages)
- Multi-currency support
- Account reconciliation workflow

## User Stories

1. As a user, I want to create multiple checking accounts so I can track balances separately
2. As a user, I want to see current balances for all my accounts in one place
3. As a user, I want to record transactions against specific accounts, not just account types
4. As a user, I want to track my 401(k) balance over time without creating fake transactions
5. As a user, I want to set an initial balance when creating an account
6. As a user, I want to update retirement account balances monthly without manual transaction entry
7. As a user, I want to see historical balance charts for each account

## Current State

### What Exists

- `AccountType` model with CSV field mappings
- `/account_types` page for managing CSV import templates
- `Transaction.account_id` references `account_types.id`
- Default account types: Chase Checking, Discover Credit, US Bank, 401k, IRA, etc.

### What's Missing

- Separate `Account` model
- Account balance tracking
- Account creation/management UI
- Historical balance snapshots
- Account categorization beyond CSV templates

## Proposed Solution

### Database Schema Changes

#### New Table: `account`

```sql
CREATE TABLE account (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,                          -- User-friendly name ("Chase Personal Checking")
    account_category ENUM('checking', 'savings', 'credit_card', 'retirement', 'brokerage', 'other') NOT NULL,
    account_type_id INT,                                 -- FK to account_type (CSV template, NULL for manual accounts)
    family_id INT NOT NULL,                              -- FK to family
    initial_balance DECIMAL(15, 2) DEFAULT 0.00,         -- Starting balance
    current_balance DECIMAL(15, 2) DEFAULT 0.00,         -- Cached current balance
    last_balance_update DATE,                            -- Last time balance was updated
    is_active BOOLEAN DEFAULT TRUE,                      -- Soft delete / archive accounts
    notes TEXT,                                          -- Optional account notes
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (account_type_id) REFERENCES account_type(id) ON DELETE SET NULL,
    FOREIGN KEY (family_id) REFERENCES family(id) ON DELETE CASCADE,
    INDEX idx_family_category (family_id, account_category),
    INDEX idx_family_active (family_id, is_active)
);
```

**Account Categories:**
- `checking`: Bank checking accounts
- `savings`: Savings accounts, CDs, money market
- `credit_card`: Credit card accounts
- `retirement`: 401(k), IRA, Roth IRA, 403(b), etc.
- `brokerage`: Taxable investment accounts
- `other`: Misc accounts (HSA, 529, etc.)

#### New Table: `account_balance_history`

Track balance snapshots over time (especially for retirement/brokerage accounts):

```sql
CREATE TABLE account_balance_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_id INT NOT NULL,                             -- FK to account
    balance DECIMAL(15, 2) NOT NULL,                     -- Balance at this point in time
    as_of_date DATE NOT NULL,                            -- Date of balance snapshot
    notes TEXT,                                          -- Optional notes (e.g., "Monthly statement")
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES account(id) ON DELETE CASCADE,
    UNIQUE KEY unique_account_date (account_id, as_of_date),
    INDEX idx_account_date (account_id, as_of_date)
);
```

**Purpose:**
- Store periodic balance updates for accounts
- Historical balance charts
- Track retirement account growth without fake transactions

#### Updated Table: `transaction`

Add foreign key to new `account` table:

```sql
-- Add new column
ALTER TABLE transaction
ADD COLUMN account_id_new INT AFTER account_id;

-- Add foreign key
ALTER TABLE transaction
ADD CONSTRAINT fk_transaction_account
FOREIGN KEY (account_id_new) REFERENCES account(id) ON DELETE RESTRICT;

-- Rename columns (after migration)
ALTER TABLE transaction CHANGE account_id account_type_id INT;
ALTER TABLE transaction CHANGE account_id_new account_id INT;
```

**Migration Strategy:**
1. Add `account_id_new` column (nullable)
2. Create default accounts for each existing AccountType
3. Backfill `account_id_new` based on `transaction.account_id` → `account_type.id`
4. Make `account_id_new` NOT NULL
5. Rename columns: `account_id` → `account_type_id`, `account_id_new` → `account_id`

**Final Schema:**
```python
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    account_type_id = db.Column(db.Integer, db.ForeignKey("account_types.id"))  # CSV template (NULL for manual)
    account_id = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=False)  # Actual account
    is_transfer = db.Column(db.Boolean, default=False)
```

### User Interface

#### New Page: `/accounts` - Account List

Main account management page showing all accounts:

```
Accounts Overview
-----------------
Total Net Worth: $52,450.75

[+ Add Account]

Checking Accounts                            $3,250.50
├─ Chase Personal Checking     $2,150.00    [View] [Edit]
└─ Ally Online Checking        $1,100.50    [View] [Edit]

Savings Accounts                             $15,200.25
├─ Marcus High-Yield Savings   $12,000.00   [View] [Edit]
├─ Emergency Fund              $3,000.00    [View] [Edit]
└─ Travel Fund CD              $200.25      [View] [Edit]

Credit Cards                                 -$1,250.00
└─ Discover It                 -$1,250.00   [View] [Edit]

Retirement Accounts                          $35,250.00
├─ 401(k) - Employer           $25,000.00   [View] [Edit]
├─ Traditional IRA - Vanguard  $7,500.00    [View] [Edit]
└─ Roth IRA - Fidelity         $2,750.00    [View] [Edit]

[View Net Worth Report] [Account History]
```

**Features:**
- Grouped by account category
- Current balances displayed
- Color coding (positive = green, negative = red for credit cards)
- Quick actions: View details, Edit, Archive
- Total net worth calculation

#### New Page: `/accounts/add` - Add Account Form

```
Add New Account
---------------
Name: [________________________]
      (e.g., "Chase Personal Checking")

Category: [Checking ▼]
          Options: Checking, Savings, Credit Card, Retirement, Brokerage, Other

Link to CSV Import Template (optional):
[Choose Account Type ▼]
(None) - Manual entry only
Chase Checking
Discover Credit Card
...

Initial Balance: [$__________]
                 Current balance as of today

Notes: [________________________]
       (Optional account notes)

[Save Account] [Cancel]
```

**Validation:**
- Name required, unique within family
- Category required
- Initial balance defaults to $0.00
- account_type_id optional (for manual accounts or retirement accounts)

#### New Page: `/accounts/<id>` - Account Details

```
Chase Personal Checking
-----------------------
Category: Checking
Current Balance: $2,150.00
Last Updated: 2025-12-20
Status: Active

[Update Balance] [Edit Account] [View Transactions] [Archive]

Recent Transactions
-------------------
Date       Description              Category        Amount      Balance
2025-12-20 Grocery Store           Groceries       -$45.23     $2,150.00
2025-12-19 Paycheck                Salary          +$2,500.00  $2,195.23
2025-12-18 Electric Bill           Utilities       -$120.00    -$304.77
...

[View All Transactions for This Account]

Balance History (Last 6 Months)
--------------------------------
[Line chart showing balance over time]

Month      Balance
Dec 2025   $2,150.00
Nov 2025   $1,980.50
Oct 2025   $2,100.25
...
```

**For Retirement/Brokerage Accounts:**
```
401(k) - Employer Plan
----------------------
Category: Retirement
Current Balance: $25,000.00
Last Updated: 2025-12-15

[Update Balance] [Edit Account]

Balance History
---------------
[Line chart showing growth over time]

Date         Balance      Change       Notes
2025-12-15   $25,000.00   +$1,200.00   Q4 contribution + gains
2025-11-15   $23,800.00   +$850.00     Monthly contribution
2025-10-15   $22,950.00   +$800.00     Monthly contribution
...

[Add Balance Update]

Related Transactions (Contributions)
------------------------------------
Date       Description              Amount
2025-12-15 401k Contribution       -$500.00
2025-11-15 401k Contribution       -$500.00
...
```

#### New Page: `/accounts/<id>/update_balance` - Update Account Balance

For retirement/brokerage accounts (or manual balance corrections):

```
Update Account Balance
----------------------
Account: 401(k) - Employer Plan

Current Balance: $25,000.00 (as of 2025-11-15)

New Balance: [$__________]
As of Date:  [2025-12-15]
Notes:       [Q4 contribution + market gains]

[Save Balance Update] [Cancel]
```

**Behavior:**
- Creates entry in `account_balance_history`
- Updates `account.current_balance` and `account.last_balance_update`
- Shows change amount (new - old)
- Optional notes field

#### Updated Page: `/transactions/add` - Add Transaction

Modified to select from actual accounts:

```
Add Transaction
---------------
Date:        [2025-12-20]
Amount:      [$__________]
Type:        ● Expense  ○ Income  ○ Transfer
Description: [________________________]
Category:    [Groceries ▼]
Account:     [Chase Personal Checking ▼]  ← Changed from "Account Type"
             Options grouped by category:
             Checking Accounts
               - Chase Personal Checking
               - Ally Online Checking
             Savings Accounts
               - Marcus High-Yield Savings
             Credit Cards
               - Discover It

[Save Transaction] [Cancel]
```

**Changes:**
- Dropdown now shows accounts, not account types
- Accounts grouped by category
- Only show active accounts
- For transfers: Add "To Account" dropdown

#### Updated Page: `/transactions/import` - CSV Import

Modified to link imported transactions to accounts:

```
Import Transactions from CSV
----------------------------
Select CSV File: [Choose File]

CSV Template: [Chase Checking ▼]  ← Still select AccountType (defines CSV format)

Import Into Account: [Chase Personal Checking ▼]  ← NEW: Select actual account
                     Options filtered by account_type_id or show all

[Upload and Preview]
```

**Behavior:**
- AccountType still defines CSV parsing
- Transactions assigned to selected Account
- Could auto-select account if only one matches the AccountType

#### Updated Page: `/account_types` - CSV Import Templates

Keep existing page, but clarify purpose:

```
CSV Import Templates
--------------------
These templates define how to parse CSV files from different banks.
To manage your actual accounts, go to [Accounts →](/accounts).

[+ Add Import Template]

Name                 Date Field    Amount Field    Description Field    Actions
Chase Checking       Date          Amount          Description          [Edit] [Delete]
Discover Credit      Trans. Date   Amount          Description          [Edit] [Delete]
...
```

**Changes:**
- Add clarifying text at top
- Link to new `/accounts` page
- Rename navigation from "Account Types" to "CSV Templates" (optional)

### API Endpoints

#### Account Management

```python
# List accounts
GET /api/accounts
Response: [{"id": 1, "name": "Chase Personal Checking", "category": "checking", "current_balance": 2150.00, ...}, ...]

# Get single account
GET /api/accounts/<id>
Response: {"id": 1, "name": "Chase Personal Checking", "category": "checking", "current_balance": 2150.00, ...}

# Create account
POST /api/accounts
Body: {"name": "New Checking", "account_category": "checking", "account_type_id": 1, "initial_balance": 500.00}
Response: {"id": 2, "name": "New Checking", ...}

# Update account
PUT /api/accounts/<id>
Body: {"name": "Updated Name", "notes": "New notes"}
Response: {"id": 1, "name": "Updated Name", ...}

# Archive account (soft delete)
POST /api/accounts/<id>/archive
Response: {"success": true}

# Restore archived account
POST /api/accounts/<id>/restore
Response: {"success": true}

# Delete account (hard delete, only if no transactions)
DELETE /api/accounts/<id>
Response: {"success": true}
```

#### Balance History

```python
# Get balance history
GET /api/accounts/<id>/balance_history?start_date=2024-01-01&end_date=2025-12-20
Response: [{"id": 1, "balance": 25000.00, "as_of_date": "2025-12-15", "notes": "Q4 update"}, ...]

# Add balance update
POST /api/accounts/<id>/balance
Body: {"balance": 25500.00, "as_of_date": "2025-12-20", "notes": "End of month"}
Response: {"id": 2, "account_id": 1, "balance": 25500.00, ...}

# Update balance entry
PUT /api/balance_history/<id>
Body: {"balance": 25600.00, "notes": "Corrected amount"}
Response: {"id": 2, "balance": 25600.00, ...}

# Delete balance entry
DELETE /api/balance_history/<id>
Response: {"success": true}
```

#### Account Balance Calculation

```python
# Get calculated balance for transaction-based accounts
GET /api/accounts/<id>/calculated_balance?as_of_date=2025-12-20
Response: {"account_id": 1, "balance": 2150.00, "as_of_date": "2025-12-20", "transaction_count": 145}

# Recalculate current balance (sum all transactions)
POST /api/accounts/<id>/recalculate_balance
Response: {"account_id": 1, "old_balance": 2100.00, "new_balance": 2150.00, "updated": true}
```

## Implementation Plan

### Phase 1: Database Migration and Models

**Tasks:**
- [ ] Create `account` table migration
- [ ] Create `account_balance_history` table migration
- [ ] Create `Account` model with relationships
- [ ] Create `AccountBalanceHistory` model
- [ ] Add migration to update `transaction` table (add `account_id_new` column)
- [ ] Create data migration to backfill accounts from AccountTypes
- [ ] Add model tests (account creation, balance updates, relationships)

**Database Migration Strategy:**
```python
# Migration 1: Create account table
def upgrade():
    op.create_table('account', ...)
    op.create_table('account_balance_history', ...)

# Migration 2: Add account_id_new to transaction
def upgrade():
    op.add_column('transaction', sa.Column('account_id_new', sa.Integer))
    op.create_foreign_key('fk_transaction_account', 'transaction', 'account', ['account_id_new'], ['id'])

# Migration 3: Data migration - create accounts from account_types
def upgrade():
    # For each AccountType, create a corresponding Account
    connection = op.get_bind()
    account_types = connection.execute(text("SELECT * FROM account_types"))

    for at in account_types:
        # Determine category from account type name
        category = determine_category(at.name)  # "401k" -> "retirement", "Checking" -> "checking"

        connection.execute(text("""
            INSERT INTO account (name, account_category, account_type_id, family_id, initial_balance, current_balance)
            VALUES (:name, :category, :id, :family_id, 0.00, 0.00)
        """), {"name": at.name, "category": category, "id": at.id, "family_id": at.family_id})

# Migration 4: Backfill transaction.account_id_new from account_type_id
def upgrade():
    connection = op.get_bind()
    connection.execute(text("""
        UPDATE transaction t
        INNER JOIN account a ON t.account_id = a.account_type_id
        SET t.account_id_new = a.id
    """))

# Migration 5: Rename columns
def upgrade():
    op.alter_column('transaction', 'account_id', new_column_name='account_type_id')
    op.alter_column('transaction', 'account_id_new', new_column_name='account_id')
    op.alter_column('transaction', 'account_id', nullable=False)
```

**Testing:**
- Verify backward compatibility (existing transactions still work)
- Test account creation for each category
- Test balance history CRUD operations

### Phase 2: Backend Services and API

**Tasks:**
- [ ] Create `AccountService` with CRUD operations
- [ ] Create `BalanceHistoryService`
- [ ] Implement balance calculation for transaction-based accounts
- [ ] Create API endpoints for accounts
- [ ] Create API endpoints for balance history
- [ ] Add service tests (balance calculations, category filtering, family scoping)
- [ ] Update transaction service to handle new account relationship

**Service Methods:**
```python
# app/services/account_service.py
def create_account(name, category, family_id, account_type_id=None, initial_balance=0.00, notes=None):
    """Create new account with optional initial balance."""
    account = Account(...)
    db.session.add(account)

    # If initial_balance != 0, create balance history entry
    if initial_balance != 0:
        create_balance_history(account.id, initial_balance, date.today(), "Initial balance")

    db.session.commit()
    return account

def get_accounts_by_category(family_id, category=None, active_only=True):
    """Get accounts grouped by category."""
    query = Account.query.filter_by(family_id=family_id)
    if category:
        query = query.filter_by(account_category=category)
    if active_only:
        query = query.filter_by(is_active=True)
    return query.all()

def calculate_transaction_balance(account_id, as_of_date=None):
    """Calculate balance by summing all transactions."""
    query = Transaction.query.filter_by(account_id=account_id)
    if as_of_date:
        query = query.filter(Transaction.timestamp <= as_of_date)

    total = db.session.query(func.sum(Transaction.amount)).filter(...).scalar() or 0
    return total + account.initial_balance

def update_account_balance(account_id, new_balance, as_of_date, notes=None):
    """Update account balance (for retirement/brokerage accounts)."""
    account = Account.query.get(account_id)

    # Create balance history entry
    history = AccountBalanceHistory(
        account_id=account_id,
        balance=new_balance,
        as_of_date=as_of_date,
        notes=notes
    )
    db.session.add(history)

    # Update current balance
    account.current_balance = new_balance
    account.last_balance_update = as_of_date
    db.session.commit()

    return history
```

### Phase 3: User Interface

**Tasks:**
- [ ] Create `/accounts` page (account list)
- [ ] Create `/accounts/add` page (add account form)
- [ ] Create `/accounts/<id>` page (account details)
- [ ] Create `/accounts/<id>/edit` page (edit account form)
- [ ] Create `/accounts/<id>/update_balance` page (balance update form)
- [ ] Update `/transactions/add` page (select from accounts)
- [ ] Update `/transactions/import` page (select account + account type)
- [ ] Update `/account_types` page (clarify as CSV templates)
- [ ] Add navigation link to accounts page
- [ ] Create templates with Bootstrap styling
- [ ] Add Chart.js balance history charts

**Key Templates:**
```
app/templates/accounts/
├── index.html              # Account list grouped by category
├── add_account.html        # Add new account form
├── edit_account.html       # Edit account form
├── account_details.html    # Account details + transactions + balance history
└── update_balance.html     # Update balance form (retirement/brokerage)
```

**Navigation Updates:**
```html
<!-- app/templates/base.html -->
<nav>
  <a href="{{ url_for('dashboard') }}">Dashboard</a>
  <a href="{{ url_for('transactions.index') }}">Transactions</a>
  <a href="{{ url_for('accounts.index') }}">Accounts</a>  <!-- NEW -->
  <a href="{{ url_for('budgets.index') }}">Budgets</a>
  <a href="{{ url_for('reports.monthly') }}">Reports</a>
  <div class="dropdown">Admin
    <a href="{{ url_for('categories.index') }}">Categories</a>
    <a href="{{ url_for('account_types.index') }}">CSV Templates</a>  <!-- Renamed -->
    <a href="{{ url_for('import_rules.index') }}">Import Rules</a>
  </div>
</nav>
```

### Phase 4: Testing and Polish

**Tasks:**
- [ ] Integration tests for account CRUD operations
- [ ] Integration tests for balance history
- [ ] Integration tests for updated transaction flow
- [ ] UI/UX refinements (loading states, error messages)
- [ ] Performance testing (large account lists, many transactions)
- [ ] Documentation updates (user guide, API docs)
- [ ] Migration guide for existing users
- [ ] Changelog entry

**Test Scenarios:**
- Create account → Add transactions → Verify calculated balance
- Create retirement account → Add balance updates → Verify balance history chart
- Import CSV → Verify transactions linked to correct account
- Archive account → Verify hidden from lists but transactions still accessible
- Multiple accounts of same type → Verify separate balances
- Family isolation → Verify cannot access other family's accounts

### Phase 5: Dashboard Integration

**Tasks:**
- [ ] Update dashboard to show account balances
- [ ] Add account balance widget
- [ ] Update net worth calculation to include all accounts
- [ ] Add account balance trend chart
- [ ] Performance optimization for dashboard queries

## Technical Considerations

### Balance Calculation Strategy

Two types of accounts require different balance calculation approaches:

#### Transaction-Based Accounts (Checking, Savings, Credit Cards)

Balance = `initial_balance` + SUM(transactions)

```python
def get_current_balance(account):
    if account.account_category in ['checking', 'savings', 'credit_card']:
        transaction_sum = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.account_id == account.id
        ).scalar() or 0
        return account.initial_balance + transaction_sum
    else:
        # For retirement/brokerage, use latest balance history entry
        latest = AccountBalanceHistory.query.filter_by(
            account_id=account.id
        ).order_by(AccountBalanceHistory.as_of_date.desc()).first()

        return latest.balance if latest else account.initial_balance
```

#### Value-Based Accounts (Retirement, Brokerage)

Balance = latest entry in `account_balance_history`

**Why Different?**
- Retirement accounts grow via contributions + market gains
- Creating fake transactions for market gains is misleading
- Periodic balance snapshots are more accurate
- Users update balances monthly from statements

### Migration Path for Existing Users

1. **Pre-Migration**:
   - Existing transactions reference `account_types.id`
   - No separate account concept

2. **Post-Migration**:
   - Create one `Account` per `AccountType` (default migration)
   - All transactions now reference `account.id`
   - Users can create additional accounts of same type

3. **User Experience**:
   - Seamless: Existing transactions still work
   - New feature: Can add multiple accounts
   - Gradual adoption: Can keep using single account per type

**Example:**
```
Before Migration:
  AccountType: "Chase Checking" (id=1)
  Transactions: account_id=1 (points to AccountType)

After Migration:
  AccountType: "Chase Checking" (id=1, still exists for CSV import)
  Account: "Chase Checking" (id=1, account_type_id=1)
  Transactions: account_type_id=1 (CSV template), account_id=1 (actual account)

User Adds Second Account:
  Account: "Chase Business Checking" (id=2, account_type_id=1)
  New Transactions: account_type_id=1 (same CSV format), account_id=2 (different account)
```

### Account Categories Mapping

Help users choose category during account creation:

| Account Type Name (from defaults) | Suggested Category |
|-----------------------------------|-------------------|
| Chase Checking, US Bank Checking | checking |
| Marcus Savings, US Bank Savings | savings |
| Discover Credit, Chase Credit | credit_card |
| 401k Account, 403b Account | retirement |
| Traditional IRA, Roth IRA | retirement |
| (User creates manually) | brokerage |
| HSA, 529 Plan | other |

**Migration Function:**
```python
def determine_category(account_type_name):
    """Auto-detect category from AccountType name."""
    name_lower = account_type_name.lower()

    if 'checking' in name_lower:
        return 'checking'
    elif 'savings' in name_lower:
        return 'savings'
    elif 'credit' in name_lower:
        return 'credit_card'
    elif any(term in name_lower for term in ['401k', '403b', 'ira', 'roth']):
        return 'retirement'
    elif 'brokerage' in name_lower:
        return 'brokerage'
    else:
        return 'other'
```

### Performance Optimization

1. **Cache Current Balances**:
   - Store `current_balance` in `account` table
   - Update on transaction add/edit/delete
   - Recalculate on demand if out of sync

2. **Index Strategy**:
   - `idx_family_category` for account list page
   - `idx_family_active` for filtering archived accounts
   - `idx_account_date` for balance history queries

3. **Dashboard Query Optimization**:
   - Single query to get all account balances
   - Aggregate by category in SQL
   - Cache account list per family

## Open Questions

1. **Should we support account transfers?**
   - Link two transactions with `is_transfer=True`?
   - Create dedicated Transfer model?
   - **Recommendation**: Defer to Phase 2, keep existing transfer flag for now

2. **How to handle credit card payments?**
   - Transfer from checking to credit card account?
   - Special transaction type?
   - **Recommendation**: Use transfer between checking and credit_card accounts

3. **Should archived accounts show in dropdowns?**
   - Hide from transaction entry dropdowns?
   - Show in reports if they have historical transactions?
   - **Recommendation**: Hide from dropdowns, show in "View All Accounts (including archived)" toggle

4. **Initial balance vs historical balance?**
   - Is `initial_balance` the balance when account was added to FRacker?
   - Or the balance when account was opened at the bank?
   - **Recommendation**: Balance when added to FRacker (clearer for users)

5. **Automatic balance calculation vs manual?**
   - For checking/savings, auto-calculate or let users override?
   - **Recommendation**: Auto-calculate by default, add "manual override" flag if needed in Phase 2

6. **Should AccountType be required for all accounts?**
   - What if user doesn't import CSVs, only manual entry?
   - **Recommendation**: Make `account_type_id` optional (NULL = manual account)

## Alternatives Considered

### Option 1: Keep AccountType Dual Purpose

**Approach:** Extend AccountType with balance tracking instead of creating separate Account model

**Pros:**
- Less migration complexity
- Fewer database changes
- Existing code mostly works

**Cons:**
- Still can't have multiple accounts of same type
- Confusing semantics persist
- Harder to add features like retirement tracking
- Technical debt increases

**Decision:** Rejected - doesn't solve core problem

### Option 2: Single "Balance Snapshot" Table for All Accounts

**Approach:** Use `account_balance_history` for ALL accounts, including checking/savings

**Pros:**
- Unified balance tracking approach
- Consistent data model

**Cons:**
- Expensive for transaction-heavy accounts (daily snapshots = lots of rows)
- Redundant data (can calculate from transactions)
- More complex queries

**Decision:** Rejected - use hybrid approach (calculate for transaction accounts, snapshot for value accounts)

### Option 3: Separate Models for Different Account Types

**Approach:** `CheckingAccount`, `RetirementAccount`, `BrokerageAccount` models

**Pros:**
- Type-safe, clear separation
- Different fields per account type

**Cons:**
- Over-engineering for current needs
- Harder to query across all accounts
- More migration complexity

**Decision:** Rejected - single `Account` model with `account_category` enum is simpler

## Dependencies

- **Depends On:** None (foundational feature)
- **Required By:**
  - [retirement-accounts.md](retirement-accounts.md) - Enhanced retirement tracking
  - [asset-management.md](asset-management.md) - Net worth calculation

## Success Metrics

1. **Functionality:**
   - Users can create multiple accounts of the same type
   - Balance calculations are accurate
   - CSV import works with new account selection
   - Zero data loss during migration

2. **Performance:**
   - Account list page loads in <1s
   - Balance calculations <500ms
   - Dashboard shows account summary without slowdown

3. **User Experience:**
   - Clear separation between "CSV Templates" and "Accounts"
   - Intuitive account creation flow
   - Historical balance charts are readable

4. **Code Quality:**
   - >80% test coverage on new code
   - No breaking changes to existing features
   - Clean migration path for existing data

---

*This feature provides the foundation for comprehensive financial tracking in FRacker, enabling future enhancements for retirement and asset management.*
