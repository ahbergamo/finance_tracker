# Accounts

Accounts in FRacker represent your bank accounts, credit cards, retirement accounts, and investment accounts. This guide explains the different account types and how to configure them.

## Account Types

FRacker supports five types of accounts:

| Type | Description | Balance Tracking |
|------|-------------|------------------|
| **Checking** | Bank checking accounts | Transaction-based |
| **Savings** | Bank savings accounts | Transaction-based |
| **Credit Card** | Credit card accounts | Transaction-based |
| **Retirement** | 401(k), IRA, 403(b), etc. | Balance history |
| **Brokerage** | Investment/brokerage accounts | Balance history |

### Transaction-Based vs Balance History

**Transaction-based accounts** (checking, savings, credit cards) calculate their balance from imported transactions. You upload CSV files from your bank, and FRacker calculates the balance.

**Balance history accounts** (retirement, brokerage) track balances you manually enter over time. This is ideal for accounts where you care about the total balance rather than individual transactions (like 401k statements).

## CSV Import Configuration

For transaction-based accounts, you configure how FRacker parses CSV files from your bank:

- Which CSV column contains transaction dates
- Which column has the transaction amount
- Which column has the description/merchant name
- Whether positive values are expenses or income

Different banks use different CSV formats, so you'll need to configure each account's CSV settings.

## Pre-Configured Account Types

FRacker includes templates for popular banks:

- **Chase Checking**
- **Chase Credit Card**
- **Bank of America**
- **Wells Fargo**
- **Capital One**
- **Citi Credit Card**

You can use these as-is or customize them for your needs.

## Creating a Custom Account Type

### Step 1: Export a Sample CSV

1. Log into your bank
2. Export a transaction statement as CSV
3. Open the CSV in a text editor or Excel
4. Note the column names in the header row

Example CSV:
```csv
Transaction Date,Description,Amount,Balance,Type
12/20/2025,STARBUCKS #1234,-5.50,1245.50,DEBIT
12/21/2025,PAYCHECK DEPOSIT,2000.00,3245.50,CREDIT
```

### Step 2: Create Account Type

1. Navigate to **Settings → Account Types**
2. Click **Add Account Type**
3. Fill in the configuration

### Step 3: Configure Fields

| Field | Purpose | Example |
|-------|---------|---------|
| **Name** | Descriptive name for this account | "Chase Personal Checking" |
| **Date Field** | CSV column name for date | "Transaction Date" |
| **Amount Field** | CSV column name for amount | "Amount" |
| **Description Field** | CSV column for merchant/description | "Description" |
| **Category Field** | Bank's category column (optional) | "Type" |
| **Positive = Expense** | Check if positive amounts are expenses | ☑ or ☐ |

### Step 4: Test the Configuration

1. Save the Account Type
2. Try importing a CSV file
3. Check the preview to ensure fields are parsed correctly
4. Adjust if needed

## Field Configuration Examples

### Example 1: Chase Checking

Chase uses positive values for deposits (income):

```
Name: Chase Checking
Date Field: Transaction Date
Amount Field: Amount
Description Field: Description
Category Field: Type
Positive = Expense: ☐ (unchecked)
```

**CSV Format:**
```csv
Transaction Date,Description,Amount,Type
12/20/2025,Coffee Shop,-5.50,Purchase
12/21/2025,Paycheck,2000.00,Deposit
```

### Example 2: Credit Card (Positive = Expense)

Many credit cards show charges as positive numbers:

```
Name: Citi Credit Card
Date Field: Date
Amount Field: Amount
Description Field: Merchant
Category Field: (empty)
Positive = Expense: ☑ (checked)
```

**CSV Format:**
```csv
Date,Merchant,Amount
12/20/2025,AMAZON.COM,45.99
12/21/2025,PAYMENT RECEIVED,-100.00
```

### Example 3: Separate Debit/Credit Columns

Some banks use separate columns:

```
Name: Bank of America
Date Field: Date
Amount Field: Amount
Description Field: Description
Category Field: (empty)
Positive = Expense: ☐ (unchecked)
```

For separate debit/credit columns, combine them into a single "Amount" column before import, or configure two Account Types (one for debits, one for credits).

## Field Details

### Date Field

The column containing the transaction date.

**Common Names:**
- Date
- Transaction Date
- Post Date
- Effective Date
- Trans. Date

**Supported Formats:**
- MM/DD/YYYY
- YYYY-MM-DD
- DD/MM/YYYY
- Month DD, YYYY

### Amount Field

The column with the transaction amount.

**Common Names:**
- Amount
- Transaction Amount
- Debit/Credit
- Value

**Format Notes:**
- Can be positive or negative
- May include currency symbols ($)
- May use parentheses for negatives: (50.00)
- Decimals with period or comma

### Description Field

The merchant name or transaction description.

**Common Names:**
- Description
- Merchant
- Payee
- Details
- Memo

**Usage:**
- Used for import rule matching
- Displayed in transaction lists
- Searchable

### Category Field (Optional)

Your bank's category for the transaction.

**Common Names:**
- Category
- Type
- Transaction Type
- Class

**Usage:**
- Can be used for initial categorization
- Often overridden by import rules
- Not all banks provide this

### Positive = Expense Checkbox

Determines how FRacker interprets positive vs. negative values.

**When to Check:**
- Credit card statements (charges are positive)
- Some banks show expenses as positive
- When deposits/credits are negative

**When to Uncheck:**
- Standard checking account format
- Expenses are negative, income is positive
- Most common configuration

## Advanced Configuration

### Multiple Accounts, Same Bank

If you have multiple accounts at the same bank:

**Option 1:** One Account Type, Multiple Imports
- Use the same Account Type for all accounts
- Import each account's CSV separately
- Categorize or tag to differentiate

**Option 2:** Separate Account Types
- Create one Account Type per account
- Name them descriptively ("Chase Checking", "Chase Savings")
- Easier to track which CSV came from which account

### Date Format Issues

If dates aren't parsing correctly:

1. Check the exact column name (case-sensitive)
2. Verify date format in CSV
3. Try different date field if bank has multiple date columns
4. Manually standardize dates before import if needed

### Amount in Multiple Columns

If debits and credits are separate:

**Workaround:**
1. Open CSV in Excel/Sheets
2. Create new "Amount" column
3. Formula: `=IF(ISBLANK(C2), D2, -C2)` (adjust columns)
4. Export as new CSV
5. Import using combined amount column

## Managing Account Types

### Editing

1. Click **Edit** next to an Account Type
2. Modify fields
3. Click **Save**

!!! warning
    Changing an Account Type affects future imports but doesn't update past transactions.

### Deleting

1. Click **Delete** next to an Account Type
2. Confirm deletion

!!! danger
    You cannot delete Account Types that have been used for past imports. Deactivate them instead by renaming (add "- INACTIVE").

### Testing Changes

After editing an Account Type:

1. Export a new CSV from your bank
2. Try importing it
3. Review the preview
4. Verify all fields parse correctly

## Troubleshooting

### Field Not Found

**Error:** "Date field 'Transaction Date' not found in CSV"

**Solutions:**
- Open CSV and check exact column name
- Check for extra spaces
- Ensure column name is in first row
- Case-sensitive matching

### Wrong Amounts

If amounts are incorrect:

- Check "Positive = Expense" setting
- Verify amount column name
- Look for currency symbols or formatting
- Check for parentheses notation

### Dates Not Parsing

If dates show as errors:

- Verify date column name
- Check date format in CSV
- Ensure dates are in a recognized format
- Try different date column if multiple exist

### Categories Not Importing

If bank categories aren't coming through:

- Verify Category Field is set correctly
- Check that column exists in CSV
- Leave blank if bank doesn't provide categories
- Use import rules instead for better control

## Best Practices

1. **Test First** - Always test with a small CSV before importing months of data
2. **Descriptive Names** - Use clear names like "Chase Personal Checking" not just "Chase"
3. **Document Settings** - Keep notes on which settings work for each bank
4. **Regular Review** - Banks sometimes change CSV formats - review periodically
5. **Backup** - Export your data before making major Account Type changes

## Retirement & Brokerage Accounts

Retirement and brokerage accounts work differently from checking/savings/credit card accounts. Instead of importing transactions, you manually track balance snapshots over time.

### Creating a Retirement Account

1. Navigate to **Settings → Accounts**
2. Click **Add Account**
3. Select **Retirement** as the Account Type
4. Choose the retirement type:
   - Traditional 401(k)
   - Roth 401(k)
   - Traditional IRA
   - Roth IRA
   - SEP IRA
   - 403(b)
5. Enter an **Initial Balance** (optional)
6. Click **Save**

CSV fields are optional for retirement accounts since you'll track balances manually.

### Creating a Brokerage Account

1. Navigate to **Settings → Accounts**
2. Click **Add Account**
3. Select **Brokerage** as the Account Type
4. Enter an **Initial Balance** (optional)
5. Click **Save**

### Adding Balance History

For retirement and brokerage accounts, you track balances over time:

1. Go to **Settings → Accounts**
2. Click the **graph icon** next to your retirement/brokerage account
3. Enter the **date** and **balance**
4. Add optional **notes**
5. Click **Add Balance**

You can add balance entries whenever you receive a statement or want to track changes. These entries are used to:

- Show current balance on the Net Worth report
- Track balance growth over time
- Calculate historical net worth

### Viewing Balance History

1. Go to **Settings → Accounts**
2. Click the **graph icon** next to the account
3. View all balance entries in the table
4. Delete entries if needed

### Net Worth Report

All account balances (transaction-based and balance history) are combined in the **Reports → Net Worth** report, which shows:

- Total assets and liabilities
- Net worth calculation
- 12-month trend chart
- Breakdown by account type

## Next Steps

- [Import Transactions](importing-transactions.md) using your configured Account Type
- [Create Import Rules](import-rules.md) for automatic categorization
- [View the Configuration Guide](../getting-started/configuration.md#account-types) for more examples
