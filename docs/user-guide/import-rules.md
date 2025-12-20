# Import Rules

Automate transaction categorization with Import Rules. Save time and ensure consistent categorization across all your imports.

![Import Rules](../assets/screenshots/Import_Rules.png)

## What Are Import Rules?

Import Rules automatically assign categories to transactions based on pattern matching. When you import a CSV file, FRacker applies these rules to categorize transactions without manual intervention.

**Benefits:**
- **Time Savings** - No manual categorization needed
- **Consistency** - Same merchants always get same category
- **Accuracy** - Reduce human error
- **Efficiency** - Process hundreds of transactions instantly

## How Import Rules Work

1. You import a CSV file
2. FRacker reads each transaction description
3. Rules are checked in order (first match wins)
4. If a pattern matches, the category is automatically assigned
5. Unmatched transactions get a default category

### Rule Matching

- **Case-insensitive** - "starbucks" matches "STARBUCKS" and "Starbucks"
- **Partial matches** - "star" matches "Starbucks Coffee #1234"
- **First match wins** - Once a rule matches, no further rules are checked
- **Order matters** - More specific rules should come before general ones

## Creating Import Rules

### Step 1: Navigate to Import Rules

1. Go to **Settings → Import Rules**
2. Click **Add Import Rule**

### Step 2: Configure the Rule

| Field | Description | Example |
|-------|-------------|---------|
| **Field to Match** | Which transaction field to check | "Description" |
| **Match Pattern** | Text to search for | "starbucks" |
| **Category** | Category to assign | "Dining Out" |
| **Is Transfer** | Mark as transfer between accounts | ☐ or ☑ |

### Step 3: Save and Test

1. Click **Save Rule**
2. Import a test CSV
3. Verify the rule works as expected
4. Adjust if needed

## Rule Examples

### Basic Categorization

**Coffee Shops:**
```
Field to Match: Description
Match Pattern: starbucks
Category: Dining Out
Is Transfer: ☐
```

Matches: "STARBUCKS #1234", "Starbucks Coffee", "STARBUCKS RESERVE"

**Gas Stations:**
```
Field to Match: Description
Match Pattern: shell
Category: Transportation - Gas
Is Transfer: ☐
```

Matches: "SHELL GAS STATION", "Shell #12345", "SHELL OIL"

### Income Rules

**Salary:**
```
Field to Match: Description
Match Pattern: paycheck
Category: Income - Salary
Is Transfer: ☐
```

**Freelance:**
```
Field to Match: Description
Match Pattern: upwork
Category: Income - Freelance
Is Transfer: ☐
```

### Transfer Rules

**Venmo/PayPal:**
```
Field to Match: Description
Match Pattern: venmo
Category: (any)
Is Transfer: ☑
```

**Between Accounts:**
```
Field to Match: Description
Match Pattern: transfer to savings
Category: (any)
Is Transfer: ☑
```

### Advanced Patterns

**Multiple Merchants:**

For chains with location numbers:
```
Pattern: walmart
Matches: WALMART #1234, WALMART SUPERCENTER, WALMART.COM
```

**Utilities:**
```
Pattern: electric
Category: Utilities - Electric
Matches: CITY ELECTRIC, ELECTRIC COMPANY, ELECTRIC UTILITY
```

## Rule Strategy

### Specific Before General

Order rules from most specific to most general:

```
1. "amazon prime" → Subscriptions
2. "amazon music" → Entertainment
3. "amazon" → Shopping - Online
```

Without this order, "amazon" would match first and the others would never apply.

### Common Patterns First

Put frequently-matching rules near the top for faster processing.

### One Merchant, Multiple Categories

If a merchant sells multiple categories of items:

**Option 1:** Use the most common category
```
Pattern: target
Category: Shopping - General
```

**Option 2:** Be specific with sub-patterns
```
Pattern: target pharmacy → Healthcare
Pattern: target grocery → Groceries
Pattern: target → Shopping - General
```

### Regular Expressions (Advanced)

While FRacker uses simple substring matching, you can still be strategic:

**Match Start of String:**
Use very specific patterns:
```
"shell #" matches "SHELL #1234" but not "SEASHELL SHOP"
```

**Avoid False Matches:**
Be as specific as needed:
```
"star" might match "STAR MARKET" and "STARBUCKS"
Better: "starbucks" and "star market" as separate rules
```

## Managing Import Rules

### Editing Rules

1. Find the rule in the list
2. Click **Edit**
3. Modify fields
4. Click **Save**

!!! note
    Editing a rule only affects future imports. Past transactions are not automatically updated.

### Deleting Rules

1. Click **Delete** next to a rule
2. Confirm deletion

Deleted rules won't be applied to future imports.

### Rule Order

Rules are applied in creation order. To change order:

1. Delete rules
2. Recreate in desired order

Or:

1. Note current rules
2. Delete all
3. Recreate in optimal order

## Testing Import Rules

### Test Before Full Import

1. Export a small CSV (10-20 transactions)
2. Create your rules
3. Import the test CSV
4. Review categorization in preview
5. Adjust rules as needed
6. Import full history once satisfied

### Review After Import

1. Navigate to **Transactions**
2. Filter by date range of import
3. Spot-check categories
4. Note any miscategorizations
5. Create/adjust rules for next time

## Common Scenarios

### Recurring Subscriptions

```
Pattern: netflix → Subscriptions - Streaming
Pattern: spotify → Subscriptions - Music
Pattern: gym membership → Health & Fitness
```

### Groceries

```
Pattern: kroger → Groceries
Pattern: whole foods → Groceries
Pattern: safeway → Groceries
Pattern: farmers market → Groceries
```

### Restaurants

```
Pattern: chipotle → Dining Out
Pattern: pizza → Dining Out
Pattern: restaurant → Dining Out
```

### Online Shopping

```
Pattern: amazon → Shopping - Online
Pattern: ebay → Shopping - Online
Pattern: etsy → Shopping - Online
```

## Troubleshooting

### Rule Not Matching

**Problem:** Expected rule doesn't apply

**Solutions:**
- Check spelling in pattern
- Verify field to match is correct
- Check rule isn't being overridden by earlier rule
- Test with simpler pattern
- Check for extra spaces in pattern

### Wrong Category Assigned

**Problem:** Transaction gets unexpected category

**Solutions:**
- Check for conflicting rules
- Review rule order (first match wins)
- Make patterns more specific
- Test with sample data

### Transfers Not Detected

**Problem:** Transfers counted as income/expense

**Solutions:**
- Create rule with "Is Transfer" checked
- Match common transfer descriptions
- Be specific to avoid false positives

### Too Many False Matches

**Problem:** Rule matches unintended transactions

**Solutions:**
- Make pattern more specific
- Add distinguishing characters
- Split into multiple specific rules
- Use longer match strings

## Best Practices

1. **Start Simple** - Begin with obvious patterns
2. **Test Incrementally** - Add rules one at a time
3. **Review Regularly** - Check new merchants monthly
4. **Be Specific** - Avoid overly broad patterns
5. **Document Intent** - Use clear rule naming
6. **Update As Needed** - Adjust when merchants change names
7. **Share With Family** - Coordinate rules with family members

## Advanced Tips

### Handling Name Changes

When merchants rename:

```
Old: "UBER EATS"
New: "UBER * EATS"

Create rules for both patterns to catch historical and future transactions.
```

### Seasonal Rules

For seasonal merchants:

```
"holiday market" → Shopping - Gifts (November-December)
"tax preparation" → Professional Services (January-April)
```

You may need to manually categorize or adjust after season ends.

### Multiple Locations

For chains with many locations:

```
"mcdonald's" matches all locations
No need for separate rules per location number
```

## Next Steps

- [Import Transactions](importing-transactions.md) to test your rules
- [Configure Account Types](account-types.md) for accurate parsing
- [Create Categories](categories-budgets.md#categories) for your rules to assign
- [Review Reports](reports.md) to verify categorization accuracy
