# Configuration Guide

Learn how to configure FRacker for your specific needs.

## Environment Variables

FRacker uses environment variables for configuration. These are typically set in a `.env` file.

### Core Settings

```env
# Application Secret (REQUIRED - must be unique and secret)
SECRET_KEY=your_super_secret_key_minimum_32_characters

# Flask Configuration Class
FLASK_CONFIG=config.config.PortableConfig
# Options: DevelopmentConfig, PortableConfig, ProductionConfig, TestingConfig
```

!!! danger "Security Critical"
    The `SECRET_KEY` is used for session encryption and CSRF tokens. **Never** use the default value in production. Generate a secure key:
    ```bash
    python -c 'import secrets; print(secrets.token_hex(32))'
    ```

### Database Configuration

```env
DB_USER=finance_user
DB_PASSWORD=your_secure_database_password
DB_HOST=db  # Use 'localhost' for local development
DB_PORT=3306
DB_NAME=finance_tracker
```

### Redis Configuration

```env
REDIS_URL=redis://redis:6379
# For remote Redis: redis://user:password@hostname:6379/0
```

### Application Settings

```env
# Port the application runs on
APP_PORT=1310

# Flask debug mode (development only)
FLASK_DEBUG=False
```

### SSL/HTTPS Settings

```env
# Path to SSL certificate (optional)
SSL_CERT_PATH=/path/to/cert.pem
SSL_KEY_PATH=/path/to/key.pem
```

## Configuration Classes

FRacker includes four configuration classes in `config/config.py`:

### DevelopmentConfig

For local development:
- Uses SQLite database by default
- Debug mode enabled
- Detailed error pages
- Auto-reload on code changes

### PortableConfig

For Docker deployments (default):
- MySQL/MariaDB database
- Debug mode enabled for easier troubleshooting
- Production-like but with debug features

### ProductionConfig

For production deployments:
- MySQL/MariaDB database
- Debug mode disabled
- Strict error handling
- Optimized for performance

### TestingConfig

For automated testing:
- In-memory SQLite database
- CSRF protection disabled
- Fast test execution

## Account Types

Account Types define how FRacker parses CSV files from your bank.

### Creating an Account Type

1. Navigate to **Settings → Account Types**
2. Click **Add Account Type**
3. Configure the fields:

| Field | Description | Example |
|-------|-------------|---------|
| **Name** | Descriptive name for this account | "Chase Checking" |
| **Date Field** | CSV column name for transaction date | "Date", "Trans. Date" |
| **Amount Field** | CSV column name for amount | "Amount", "Debit/Credit" |
| **Description Field** | CSV column name for description | "Description", "Merchant" |
| **Category Field** | CSV column for bank's category (optional) | "Category", "Type" |
| **Positive = Expense** | Check if positive values are expenses | ☐ or ☑ |

### Example: Chase Bank

```
Name: Chase Checking
Date Field: Transaction Date
Amount Field: Amount
Description Field: Description
Category Field: Type
Positive = Expense: ☑ (checked)
```

### Example: Bank of America

```
Name: BofA Checking
Date Field: Date
Amount Field: Amount
Description Field: Description
Category Field: (leave empty)
Positive = Expense: ☐ (unchecked)
```

### Pre-Defined Account Types

FRacker includes several pre-configured account types:

- Chase Checking
- Chase Credit Card
- Bank of America
- Wells Fargo
- Capital One
- Citi Credit Card

You can use these as templates or create custom ones.

## Import Rules

Import Rules automatically categorize transactions based on patterns.

### Creating an Import Rule

1. Navigate to **Settings → Import Rules**
2. Click **Add Import Rule**
3. Configure the rule:

| Field | Description | Example |
|-------|-------------|---------|
| **Field to Match** | Which transaction field to check | "Description" |
| **Match Pattern** | Text to search for (case-insensitive) | "starbucks" |
| **Category** | Category to assign | "Dining Out" |
| **Is Transfer** | Mark as transfer between accounts | ☐ or ☑ |

### Example Rules

```
Match: "amazon" → Category: "Shopping - Online"
Match: "shell" → Category: "Transportation - Gas"
Match: "venmo" → Mark as Transfer
Match: "paycheck" → Category: "Income - Salary"
```

### Pattern Matching

- Patterns are case-insensitive
- Partial matches work: "star" matches "Starbucks Coffee"
- Use specific patterns to avoid false matches
- Rules are applied in order of creation

## Categories

### Default Categories

FRacker includes default categories, but you can customize them:

**Income:**
- Salary
- Freelance
- Investment Income

**Expenses:**
- Groceries
- Dining Out
- Transportation
- Utilities
- Entertainment
- Healthcare

### Creating Custom Categories

1. Navigate to **Categories**
2. Click **Add Category**
3. Enter a descriptive name
4. Categories are family-scoped (shared with all family members)

### Best Practices

- Keep categories broad enough to be useful
- Avoid too many subcategories
- Use consistent naming (e.g., "Transportation - Gas" vs "Transportation - Public Transit")
- Review and consolidate categories periodically

## Budgets

### Creating a Budget

1. Navigate to **Budgets**
2. Click **Add Budget**
3. Configure:

| Field | Description |
|-------|-------------|
| **Name** | Budget name (e.g., "Monthly Food Budget") |
| **Amount** | Budget limit in dollars |
| **Start Date** | When budget period begins |
| **End Date** | When budget period ends |
| **Categories** | Which categories to include |

### Budget Strategies

**Monthly Budgets:**
```
Name: "March 2025 Food"
Amount: $800
Start: 2025-03-01
End: 2025-03-31
Categories: Groceries, Dining Out
```

**Annual Budgets:**
```
Name: "2025 Healthcare"
Amount: $5000
Start: 2025-01-01
End: 2025-12-31
Categories: Healthcare, Prescriptions, Insurance
```

## Advanced Configuration

### Custom Date Formats

If your bank uses non-standard date formats, you may need to modify the date parsing in `app/services/transactions/import_transaction.py`.

### Database Connection Pooling

For high-traffic deployments, adjust pool settings in `config/config.py`:

```python
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
}
```

### Session Timeout

Adjust session timeout in Redis configuration:

```python
PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
```

## Next Steps

- [Import Your First Transactions](../user-guide/importing-transactions.md)
- [Set Up Budgets](../user-guide/categories-budgets.md#budgets)
- [View Reports](../user-guide/reports.md)
