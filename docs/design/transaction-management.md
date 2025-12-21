# Transaction Management System

**Status:** ✅ Implemented
**Created:** 2025-12-20
**Author:** FRacker Team

## Overview

The Transaction Management system is the core of FRacker, enabling users to track income and expenses through a comprehensive transaction-based accounting system. This design document describes the currently implemented system.

### Goals

- Track all financial transactions (income, expenses, transfers)
- Categorize transactions for budgeting and reporting
- Import transactions from CSV files
- Support multiple account types (checking, savings, credit cards)
- Enable family-shared financial tracking
- Provide filtering, search, and reporting capabilities

## Current Architecture

### Database Models

#### Transaction Model

The core transaction model tracks individual financial events:

```python
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey("account_types.id"), nullable=False)
    is_transfer = db.Column(db.Boolean, default=False)
```

**Key Relationships:**
- `category` → Category (spending/income classification)
- `account` → AccountType (CSV import template, see note below)
- `user` → User (who created the transaction)

**Note:** `account_id` currently references `account_types.id`. The AccountType model serves a dual purpose as both a CSV import template and an account identifier. This will be refactored in the Account Management feature (see [account-management.md](account-management.md)).

#### Category Model

Categories organize transactions into spending/income groups:

```python
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    family_id = db.Column(db.Integer, db.ForeignKey("family.id"), nullable=False)
    is_income = db.Column(db.Boolean, default=False)
```

**Features:**
- Family-scoped (each family has their own categories)
- Income vs expense classification
- Default categories seeded on family creation
- Used for budget allocation and reporting

**Default Categories:**
- Income: Salary, Bonus, Interest, Refund, Other Income
- Expenses: Groceries, Dining Out, Transportation, Utilities, Entertainment, Healthcare, Shopping, Insurance, Taxes, Savings, Other Expenses

#### AccountType Model

Defines CSV field mappings for importing transactions:

```python
class AccountType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category_field = db.Column(db.String(100))
    date_field = db.Column(db.String(100), nullable=False)
    amount_field = db.Column(db.String(100), nullable=False)
    description_field = db.Column(db.String(100), nullable=False)
    positive_expense = db.Column(db.Boolean, default=False)
    family_id = db.Column(db.Integer, db.ForeignKey("family.id"), nullable=False)
```

**Purpose:**
- Maps CSV columns to transaction fields
- Handles different bank CSV formats (Chase, Discover, US Bank, etc.)
- `positive_expense` flag handles banks that use positive/negative amounts differently

**Current Dual Role (to be refactored):**
1. **CSV Import Template**: Defines how to parse bank CSV files
2. **Account Identifier**: Transactions link to AccountType to indicate which "account" they belong to

**Limitation:** Cannot have multiple accounts of the same type (e.g., two Chase checking accounts)

#### Budget Model

Budgets set spending limits for categories:

```python
class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    family_id = db.Column(db.Integer, db.ForeignKey("family.id"), nullable=False)
    categories = db.relationship("Category", secondary="budget_category_association")
```

**Features:**
- Many-to-many relationship with categories
- Date range support (monthly, annual, custom)
- Family-scoped
- Dashboard shows budget vs actual spending

#### ImportRule Model

Auto-categorizes transactions during CSV import:

```python
class ImportRule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pattern = db.Column(db.String(255), nullable=False)  # Regex pattern
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    priority = db.Column(db.Integer, default=0)
    family_id = db.Column(db.Integer, db.ForeignKey("family.id"), nullable=False)
```

**Features:**
- Regex pattern matching on transaction descriptions
- Priority ordering (higher priority rules apply first)
- Family-scoped
- Applied during CSV import preview

### Key Routes and Pages

#### Transaction Management

| Route | Purpose | Template |
|-------|---------|----------|
| `GET /transactions` | List all transactions with filters | `transactions/index.html` |
| `GET /transactions/add` | Add single transaction form | `transactions/add_transaction.html` |
| `POST /transactions/add` | Create new transaction | (redirect) |
| `GET /transactions/edit/<id>` | Edit transaction form | `transactions/edit_transaction.html` |
| `POST /transactions/edit/<id>` | Update transaction | (redirect) |
| `POST /transactions/delete/<id>` | Delete transaction | (redirect) |
| `GET /transactions/import` | CSV import page | `transactions/import_transactions.html` |
| `POST /transactions/upload` | Upload and preview CSV | `transactions/preview_import.html` |
| `POST /transactions/confirm_import` | Finalize CSV import | (redirect) |

**Transaction List Features:**
- Pagination (configurable items per page)
- Filtering by:
  - Date range (start/end date)
  - Category (multi-select)
  - Account type
  - Search term (description)
  - Transaction type (income/expense/transfer)
- Sorting by date, amount, category
- Bulk delete via checkboxes
- Export to CSV

#### Category Management

| Route | Purpose |
|-------|---------|
| `GET /categories` | List all categories |
| `POST /categories/add` | Create new category |
| `POST /categories/edit/<id>` | Update category |
| `POST /categories/delete/<id>` | Delete category |

#### Budget Management

| Route | Purpose |
|-------|---------|
| `GET /budgets` | List all budgets |
| `POST /budgets/add` | Create new budget |
| `POST /budgets/edit/<id>` | Update budget |
| `POST /budgets/delete/<id>` | Delete budget |

#### Account Type Management

| Route | Purpose |
|-------|---------|
| `GET /account_types` | List CSV import templates |
| `POST /account_types/add` | Create new template |
| `POST /account_types/edit/<id>` | Update template |
| `POST /account_types/delete/<id>` | Delete template |

**Note:** This page manages CSV import templates, not actual accounts. Will remain separate when Account Management feature is added.

#### Import Rules Management

| Route | Purpose |
|-------|---------|
| `GET /import_rules` | List auto-categorization rules |
| `POST /import_rules/add` | Create new rule |
| `POST /import_rules/edit/<id>` | Update rule |
| `POST /import_rules/delete/<id>` | Delete rule |
| `POST /import_rules/test` | Test pattern against sample text |

### CSV Import Flow

1. **Upload**: User selects CSV file and AccountType template
2. **Parse**: System reads CSV using field mappings from AccountType
3. **Auto-Categorize**: ImportRules apply pattern matching to descriptions
4. **Duplicate Detection**:
   - File-level: Check for duplicate rows in CSV
   - Database-level: Check for existing transactions (date + amount + description)
5. **Preview**: Display parsed transactions with categories and warnings
6. **User Review**: User can modify categories, exclude transactions
7. **Import**: Confirmed transactions saved to database
8. **Summary**: Show count of imported, skipped, duplicate transactions

**Duplicate Detection Logic:**
```python
def is_duplicate(transaction, existing_transactions):
    """Check if transaction already exists in database."""
    return any(
        t.timestamp.date() == transaction['date'] and
        abs(t.amount - transaction['amount']) < 0.01 and
        t.description == transaction['description']
        for t in existing_transactions
    )
```

### Service Layer

Business logic is separated from routes in `app/services/`:

#### Transaction Services

- **`create_transaction(data)`**: Validate and create new transaction
- **`update_transaction(id, data)`**: Update existing transaction
- **`delete_transaction(id)`**: Delete transaction (with family scope check)
- **`get_transactions_for_family(family_id, filters)`**: Query with filters
- **`calculate_balance(account_id, end_date)`**: Sum transactions up to date
- **`get_monthly_spending(family_id, month, year)`**: Category breakdown
- **`detect_duplicates(transactions, family_id)`**: Find existing matches

#### Import Services

- **`parse_csv(file, account_type)`**: Read CSV using field mappings
- **`apply_import_rules(transactions, family_id)`**: Auto-categorize
- **`validate_import(transactions)`**: Check for errors
- **`bulk_import_transactions(transactions, user_id)`**: Save multiple transactions

### Reporting System

Located in `app/routes/reports/`:

#### Monthly Report (`/reports/monthly`)

- Income vs expense breakdown by category
- Category spending charts (pie/bar)
- Month-over-month comparison
- Budget variance analysis
- Top spending categories
- Date range filter

#### Annual Report (`/reports/annual`)

- Year-to-date income/expense summary
- Monthly trend charts
- Category distribution
- Year-over-year comparison
- Savings rate calculation

#### Income/Expense Reports

- `/reports/income`: All income transactions with category breakdown
- `/reports/expense`: All expense transactions with category breakdown
- Filtering by date range, category
- Export to CSV

#### Dashboard (`/dashboard`)

- Current month income/expense summary
- Budget vs actual spending (progress bars)
- Recent transactions (last 10)
- Spending by category (pie chart)
- Monthly spending trend (line chart)
- Quick stats: total income, total expenses, net savings

### Family Scoping and Multi-User Support

All data is scoped to families to enable shared financial tracking:

**Family Model:**
```python
class Family(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
```

**User Model:**
```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    family_id = db.Column(db.Integer, db.ForeignKey("family.id"))
```

**Family Scoping Pattern:**
```python
# All queries filter by current_user.family_id
transactions = Transaction.query.join(Transaction.category).filter(
    Category.family_id == current_user.family_id
).all()
```

**Benefits:**
- Multiple users can share the same financial data
- Each family has isolated data (privacy)
- Users can only access their family's data

## Technical Implementation Details

### Authentication and Authorization

- **Flask-Login**: Session-based authentication
- **Password Hashing**: Werkzeug security (bcrypt)
- **CSRF Protection**: Flask-WTF on all forms
- **Route Protection**: `@login_required` decorator
- **Family Isolation**: All queries filter by `current_user.family_id`

### Database and Sessions

- **Production**: MySQL/MariaDB
- **Development**: SQLite
- **Sessions**: Redis-backed (REDIS_URL in config)
- **Migrations**: Alembic (Flask-Migrate)
- **ORM**: SQLAlchemy with relationships

### Frontend

- **Templates**: Jinja2 with template inheritance
- **CSS Framework**: Bootstrap 4
- **Charts**: Chart.js for dashboard visualizations
- **Forms**: Flask-WTF with server-side validation
- **Date Pickers**: HTML5 date inputs
- **Tables**: Bootstrap table styling with pagination

### Testing

- **Framework**: Pytest with fixtures
- **Database**: In-memory SQLite for speed
- **Coverage**: pytest-cov
- **CSRF**: Disabled in test config
- **Test Data**: Seeded via `tests/seed_test_data.py`

**Test Coverage:**
- Route tests for all CRUD operations
- Service layer unit tests
- CSV import flow integration tests
- Duplicate detection tests
- Family isolation tests

## Known Limitations

1. **AccountType Dual Role**: Currently serves as both CSV template and account identifier
   - Cannot have multiple accounts of the same type
   - Confusing semantics ("account" vs "import template")
   - **Resolution**: See [account-management.md](account-management.md)

2. **No Account Balances**: System doesn't track running balances
   - Balance must be calculated by summing transactions
   - No historical balance snapshots
   - **Resolution**: See [account-management.md](account-management.md)

3. **Limited Asset Tracking**: Only transaction-based accounts
   - Cannot track retirement accounts (need periodic value updates)
   - Cannot track physical assets (home, vehicles)
   - **Resolution**: See [retirement-accounts.md](retirement-accounts.md) and [asset-management.md](asset-management.md)

4. **No Reconciliation**: No bank statement reconciliation feature
   - Cannot mark transactions as "cleared" or "reconciled"
   - Relies on CSV imports for accuracy

5. **CSV Import Only**: No automated bank connections
   - Manual CSV upload required
   - No real-time transaction sync
   - (Design decision for privacy and self-hosting)

## Future Enhancements

The following features are planned or under consideration:

1. **Account Management** (🔵 In Review)
   - Separate Account model from AccountType
   - Support multiple accounts of the same type
   - Track account balances and history
   - See [account-management.md](account-management.md)

2. **Retirement Accounts** (🟡 Draft)
   - Track retirement account balances over time
   - Support 401(k), IRA, Roth IRA, etc.
   - Contribution tracking and reporting
   - See [retirement-accounts.md](retirement-accounts.md)

3. **Asset Management** (🟡 Draft)
   - Track physical assets (home, vehicles, valuables)
   - Value depreciation/appreciation over time
   - Net worth calculation
   - See [asset-management.md](asset-management.md)

4. **Advanced Reporting**
   - Tax category reporting
   - Custom date range comparisons
   - Spending patterns and trends
   - Forecast and projections

5. **Mobile Optimization**
   - Responsive design improvements
   - Mobile-first transaction entry
   - Quick expense logging

6. **Reconciliation**
   - Mark transactions as cleared
   - Bank statement reconciliation workflow
   - Balance verification

## Architecture Patterns Used

### Blueprints

Routes are organized by feature area using Flask blueprints:

```python
# app/__init__.py
from app.routes.transactions import transactions_bp
from app.routes.budgets import budgets_bp
from app.routes.categories import categories_bp

app.register_blueprint(transactions_bp)
app.register_blueprint(budgets_bp)
app.register_blueprint(categories_bp)
```

### Service Layer

Business logic is separated from routes:

```python
# Route layer (thin)
@transactions_bp.route('/transactions/add', methods=['POST'])
@login_required
def add_transaction():
    form = TransactionForm()
    if form.validate_on_submit():
        transaction = create_transaction(form.data, current_user)
        flash('Transaction added successfully.', 'success')
        return redirect(url_for('transactions.index'))
    return render_template('transactions/add.html', form=form)

# Service layer (business logic)
def create_transaction(data, user):
    transaction = Transaction(
        amount=data['amount'],
        description=data['description'],
        timestamp=data['timestamp'],
        category_id=data['category_id'],
        account_id=data['account_id'],
        user_id=user.id
    )
    db.session.add(transaction)
    db.session.commit()
    return transaction
```

### Repository Pattern (Implicit)

SQLAlchemy queries are often wrapped in service functions:

```python
def get_transactions_for_family(family_id, filters=None):
    """Get all transactions for a family with optional filters."""
    query = Transaction.query.join(Transaction.category).filter(
        Category.family_id == family_id
    )

    if filters:
        if 'start_date' in filters:
            query = query.filter(Transaction.timestamp >= filters['start_date'])
        if 'end_date' in filters:
            query = query.filter(Transaction.timestamp <= filters['end_date'])
        if 'category_id' in filters:
            query = query.filter(Transaction.category_id == filters['category_id'])

    return query.order_by(Transaction.timestamp.desc()).all()
```

## Security Considerations

1. **CSRF Protection**: All forms include CSRF tokens
2. **Password Security**: Bcrypt hashing with salt
3. **SQL Injection**: SQLAlchemy ORM prevents injection
4. **XSS Protection**: Jinja2 auto-escapes template variables
5. **Family Isolation**: All queries filter by `current_user.family_id`
6. **Session Security**: Redis-backed sessions with secure cookies
7. **Input Validation**: Flask-WTF validates all form inputs

## Performance Considerations

1. **Database Indexes**:
   - `idx_family_type` on `account_type(family_id, category_field)`
   - Foreign key indexes on all relationships
   - Composite indexes on frequently queried columns

2. **Query Optimization**:
   - Use `.join()` to avoid N+1 queries
   - Eager loading with `joinedload()` for relationships
   - Pagination on transaction lists

3. **Caching**:
   - Redis for session storage
   - Could add caching for category lists, budgets

4. **CSV Import**:
   - Stream large files (don't load entirely into memory)
   - Bulk insert for performance
   - Batch size limit (e.g., 1000 transactions per import)

---

*This document describes the current transaction management system in FRacker. For upcoming enhancements, see the related design documents.*
