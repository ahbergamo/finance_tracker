# Importing Transactions

Learn how to import bank transactions from CSV files into FRacker.

## Overview

FRacker's CSV import feature allows you to:

- Import transactions from any bank that provides CSV exports
- Automatically categorize transactions using import rules
- Detect and handle duplicate transactions
- Preview transactions before finalizing the import

## Import Process

### Step 1: Export from Your Bank

1. Log into your bank's website
2. Navigate to transaction history or statements
3. Select the date range you want to export
4. Choose **CSV** or **Excel** format (save Excel as CSV)
5. Download the file

### Step 2: Configure Account Type

Before importing, configure an Account Type for your bank's CSV format:

1. Navigate to **Settings → Account Types**
2. Click **Add Account Type** (or use a pre-configured one)
3. Fill in the mapping:
    - **Name**: Descriptive name (e.g., "Chase Checking")
    - **Date Field**: Column name for transaction date
    - **Amount Field**: Column name for amount
    - **Description Field**: Column name for merchant/description
    - **Category Field**: Bank's category column (optional)
    - **Positive = Expense**: Check if positive values are expenses

!!! example "Example: Chase Bank"
    ```
    Name: Chase Checking
    Date Field: Transaction Date
    Amount Field: Amount
    Description Field: Description
    Category Field: Type
    Positive = Expense: ☑
    ```

See the [Configuration Guide](../getting-started/configuration.md#account-types) for more examples.

### Step 3: Import the CSV

1. Navigate to **Transactions → Import**
2. Select your **Account Type** from the dropdown
3. Click **Choose File** and select your CSV
4. Click **Upload**

### Step 4: Review Import Preview

![Import Preview](../assets/screenshots/Import_Preview.png)

The preview screen shows:

- **Parsed Transactions**: All transactions from your CSV
- **Auto-Categorization**: Categories assigned by import rules (if any)
- **Duplicate Detection**: Transactions flagged as potential duplicates
- **Validation Errors**: Any issues with the data

#### Preview Columns

| Column | Description |
|--------|-------------|
| **Date** | Transaction date |
| **Description** | Merchant or transaction description |
| **Amount** | Transaction amount (negative = expense, positive = income) |
| **Category** | Auto-assigned or default category |
| **Account** | Which account this belongs to |
| **Duplicate** | Marker if this transaction already exists |

### Step 5: Make Adjustments

Before importing, you can:

- **Change Categories**: Click on a category to select a different one
- **Create Categories**: Add new categories on the fly
- **Mark as Transfer**: Identify transfers between accounts
- **Remove Duplicates**: Uncheck duplicates you don't want to import

### Step 6: Confirm Import

1. Review the preview
2. Check **Force Import Duplicates** if needed (see below)
3. Click **Import Transactions**
4. Wait for confirmation message

## Duplicate Detection

FRacker has smart duplicate detection to prevent importing the same transaction twice.

### Types of Duplicates

| Duplicate Type | Behavior | Can Force Import? |
|----------------|----------|-------------------|
| **Same File Duplicate** | Same transaction appears multiple times in the CSV | Yes ✅ |
| **Database Duplicate** | Transaction already exists in your database (same date + amount) | Requires confirmation ⚠️ |

### Handling Duplicates

**Same File Duplicates:**
- Automatically marked with a warning
- Can be imported if intentional (e.g., recurring charges)
- Check "Force Import Duplicates" to proceed

**Database Duplicates:**
- Marked with a different color/icon
- Generally should NOT be imported
- Only force import if you're certain it's a different transaction

!!! warning "Duplicate Import Warning"
    Forcing duplicate imports can create data inconsistencies. Only do this if you're sure the transaction is genuinely new.

## Automatic Categorization

If you've set up [Import Rules](import-rules.md), transactions are automatically categorized:

- Rules match based on description patterns
- First matching rule wins
- Unmatched transactions get a default category
- You can change categories in the preview

### Example Auto-Categorization

```
"STARBUCKS #1234" → Dining Out
"SHELL GAS STATION" → Transportation - Gas
"PAYCHECK DEPOSIT" → Income - Salary
"VENMO PAYMENT" → Mark as Transfer
```

## CSV Format Requirements

### Supported Date Formats

- `MM/DD/YYYY` (e.g., 12/31/2025)
- `YYYY-MM-DD` (e.g., 2025-12-31)
- `DD/MM/YYYY` (e.g., 31/12/2025)
- Month names (e.g., "December 31, 2025")

### Amount Formats

- Positive or negative numbers
- With or without currency symbols
- Comma or period as decimal separator
- Parentheses for negative amounts (e.g., "(50.00)")

### Common CSV Formats

Most banks use one of these formats:

**Format 1: Amount in Single Column**
```csv
Date,Description,Amount,Balance
12/20/2025,Coffee Shop,-5.50,1245.50
12/21/2025,Salary Deposit,2000.00,3245.50
```

**Format 2: Separate Debit/Credit Columns**
```csv
Date,Description,Debit,Credit,Balance
12/20/2025,Coffee Shop,5.50,,1245.50
12/21/2025,Salary Deposit,,2000.00,3245.50
```

**Format 3: Bank-Specific Categories**
```csv
Transaction Date,Description,Category,Amount
12/20/2025,STARBUCKS #1234,Food & Dining,-5.50
12/21/2025,EMPLOYER INC,Income,2000.00
```

## Troubleshooting

### Import Fails

**"Invalid CSV format"**
- Ensure file is actually CSV (not Excel .xlsx)
- Check that file isn't empty
- Verify column headers match your Account Type settings

**"Date parsing error"**
- Verify the date field name is correct
- Check date format in the CSV
- Try different date field if your bank uses multiple formats

**"Amount parsing error"**
- Ensure amount field name is correct
- Check for extra characters in amount column
- Verify negative amounts are marked correctly

### No Categories Assigned

If import rules aren't working:

1. Check that rules are created (Settings → Import Rules)
2. Verify the "Field to Match" setting
3. Test with a simple pattern first
4. Check rule order (first match wins)

### Duplicates Not Detected

If legitimate duplicates aren't being caught:

- Duplicate detection uses date + amount
- Same amount on different dates won't be flagged
- Slightly different amounts won't match
- This is intentional to avoid false positives

### Wrong Category Assignments

If auto-categorization is incorrect:

1. Review your import rules for conflicts
2. Make rules more specific
3. Adjust rule order (more specific rules first)
4. Manually change categories in preview before importing

## Best Practices

1. **Import Regularly** - Weekly imports keep data current and reduce duplicates
2. **Set Up Rules First** - Create import rules before first import
3. **Always Preview** - Review transactions before finalizing
4. **Check Duplicates** - Verify duplicate detection is working
5. **Consistent Account Types** - Use the same account type for each bank account
6. **Backup Before Large Imports** - Export existing data before importing months of history

## Next Steps

- [Create Import Rules](import-rules.md) for automatic categorization
- [Configure Account Types](../getting-started/configuration.md#account-types)
- [Set Up Categories](categories-budgets.md#categories)
- [View Your Dashboard](dashboard.md)
