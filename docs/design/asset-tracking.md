# Asset Tracking Design

**Status:** 🟡 Draft
**Created:** 2025-12-20
**Author:** FRacker Team

## Overview

Expand FRacker to track all personal assets beyond bank accounts and retirement funds, providing a comprehensive net worth view.

### Goals

- Track physical assets (home, vehicles, etc.)
- Monitor asset values over time
- Calculate total net worth
- Visualize asset allocation
- Support both appreciating and depreciating assets

## Asset Categories

### Real Estate
- Primary residence
- Rental properties
- Vacation homes
- Land

### Vehicles
- Cars, trucks, motorcycles
- Boats, RVs
- Depreciation tracking

### Valuables
- Jewelry
- Art and collectibles
- Electronics

### Other Assets
- Cash (physical)
- Precious metals
- Business ownership

## Requirements

### Functional Requirements

1. **Asset Management**
   - Add/edit/delete assets
   - Categorize by asset type
   - Record purchase date and original cost
   - Track current estimated value

2. **Value Updates**
   - Manual value updates
   - Historical value tracking
   - Notes for valuation changes

3. **Depreciation**
   - Automatic depreciation calculations (vehicles)
   - Custom depreciation rates
   - Override with manual values

4. **Reporting**
   - Net worth summary
   - Asset allocation pie chart
   - Value trend charts
   - Asset category breakdowns

### Non-Functional Requirements

- Fast loading (<2s for asset list)
- Mobile-responsive interface
- Privacy: all data stays local
- Family-scoped: shared assets visible to all family members

## Database Schema

### New Table: `asset`

```sql
CREATE TABLE asset (
    id INT AUTO_INCREMENT PRIMARY KEY,
    family_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    asset_type ENUM('real_estate', 'vehicle', 'investment', 'valuable', 'other') NOT NULL,
    purchase_date DATE,
    purchase_price DECIMAL(15, 2),
    current_value DECIMAL(15, 2) NOT NULL,
    depreciation_rate DECIMAL(5, 2),  -- Annual percentage
    last_updated DATE NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (family_id) REFERENCES family(id),
    INDEX idx_family_type (family_id, asset_type)
);
```

### New Table: `asset_value_history`

```sql
CREATE TABLE asset_value_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    asset_id INT NOT NULL,
    value DECIMAL(15, 2) NOT NULL,
    as_of_date DATE NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (asset_id) REFERENCES asset(id) ON DELETE CASCADE,
    UNIQUE KEY unique_asset_date (asset_id, as_of_date),
    INDEX idx_asset_date (asset_id, as_of_date)
);
```

## User Interface

### Assets Dashboard (`/assets`)

```
Assets Overview
---------------
Total Net Worth: $425,300.50

[+ Add Asset]

Real Estate                     $350,000.00  (82%)
├─ Primary Residence           $350,000.00

Vehicles                        $45,000.00   (11%)
├─ 2022 Honda Accord           $28,000.00
└─ 2019 Toyota Camry           $17,000.00

Valuables                       $30,300.50   (7%)
├─ Jewelry Collection          $20,000.00
└─ Camera Equipment            $10,300.50

[View Historical Values] [Net Worth Report]
```

### Add/Edit Asset Form

```
Add Asset
---------
Name: [________________]
Type: [Real Estate ▼]
Purchase Date: [YYYY-MM-DD]
Purchase Price: [$_________]
Current Value: [$_________]
Depreciation Rate: [____%] (optional, for vehicles)
Notes: [________________]

[Save] [Cancel]
```

### Value History View

```
Asset Value History: 2022 Honda Accord
---------------------------------------
[Update Value]

Date         Value        Change    Notes
2025-12-20  $28,000.00   -$1,500   Estimated depreciation
2025-06-15  $29,500.00   -$2,000   Kelly Blue Book
2024-12-10  $31,500.00   -$2,500   Annual update
2024-06-01  $34,000.00   N/A       Initial value

[Chart: Value over time]
```

## Implementation Plan

### Phase 1: Basic Asset Tracking
- Database schema and models
- Asset CRUD operations
- Simple asset list page
- Manual value entry

### Phase 2: Value History
- Asset value history tracking
- Historical value charts
- Value update form

### Phase 3: Net Worth Dashboard
- Combined view of all accounts + assets
- Net worth calculation
- Asset allocation charts
- Trend analysis

### Phase 4: Advanced Features
- Depreciation calculations
- Asset categories customization
- Bulk import for historical data
- Mobile optimization

## Technical Considerations

### Depreciation Calculation

For vehicles, implement straight-line depreciation:

```python
def calculate_depreciated_value(asset):
    years_owned = (date.today() - asset.purchase_date).days / 365.25
    total_depreciation = asset.purchase_price * (asset.depreciation_rate / 100) * years_owned
    estimated_value = asset.purchase_price - total_depreciation
    return max(estimated_value, 0)  # Never go below zero
```

### Net Worth Calculation

```python
def calculate_net_worth(family_id):
    # Bank accounts (from transactions)
    checking_balance = sum_account_balances(family_id, account_type='checking')
    savings_balance = sum_account_balances(family_id, account_type='savings')

    # Retirement accounts (from retirement_balance)
    retirement_total = sum_retirement_balances(family_id)

    # Assets
    assets_total = sum_asset_values(family_id)

    # Liabilities (future: track debts/loans)
    liabilities = 0

    return (checking_balance + savings_balance + retirement_total +
            assets_total - liabilities)
```

## Open Questions

1. **Should we track liabilities (debts)?**
   - Mortgages, car loans, credit card debt
   - Answer: Yes, but separate feature

2. **Automatic depreciation vs manual updates?**
   - Auto-depreciate vehicles based on rates?
   - Answer: Support both, default to auto but allow manual override

3. **Integration with existing retirement tracking?**
   - Show retirement accounts in asset view?
   - Answer: Yes, unified net worth dashboard

4. **Photo uploads for assets?**
   - Store photos of valuables for insurance?
   - Answer: Nice to have, defer to v2

5. **Asset sharing between families?**
   - Joint ownership scenarios?
   - Answer: Not initially, assume single family ownership

## Alternatives Considered

### Option 1: External Service Integration
**Approach:** Integrate with Zillow for home values, KBB for vehicles
**Pros:** Automated, accurate
**Cons:** External dependencies, privacy, API costs
**Decision:** Defer - manual entry sufficient for v1

### Option 2: Combine with Transaction System
**Approach:** Treat asset purchases as special transactions
**Pros:** Reuse existing code
**Cons:** Assets aren't transactions, confusing UX
**Decision:** Rejected - separate system needed

## Next Steps

1. Review and approve design
2. Create database migrations
3. Implement models and services
4. Build UI components
5. Testing and refinement
6. Documentation

---

*This feature will significantly expand FRacker's utility, transforming it from a transaction tracker to a comprehensive personal finance management system.*
