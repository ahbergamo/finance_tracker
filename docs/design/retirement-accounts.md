# Retirement Accounts Enhancement

**Status:** 🟡 Draft
**Created:** 2025-12-20
**Updated:** 2025-12-21
**Author:** FRacker Team
**Depends On:** [account-management.md](account-management.md)

## Overview

Enhance FRacker's retirement account tracking with contribution tracking, goal projections, and reporting. This builds upon the Account Management system which provides balance history tracking.

### Goals

- Track retirement contributions separately from market gains
- Record employer matches
- Warn when approaching IRS contribution limits
- Calculate progress toward retirement goals
- Visualize growth over time

### Non-Goals (for initial implementation)

- Real-time market data integration
- Automated brokerage imports
- Tax calculation or reporting
- Investment recommendations
- Individual holdings tracking

## Prerequisites

This feature **requires** the Account Management system (see [account-management.md](account-management.md)):

- `accounts` table with `account_type='retirement'`
- `retirement_type` field for subtypes (traditional_401k, roth_401k, etc.)
- `account_balance_history` table for balance snapshots
- Balance update UI on account detail page

## What Account Management Provides

After Account Management is implemented:
- Users can create retirement accounts with proper subtypes
- Balance snapshots are tracked in `account_balance_history`
- `/accounts/<id>` page shows balance history with edit/delete
- Balance calculation uses latest snapshot

## What This Enhancement Adds

- **Contribution tracking** - Separate from balance changes
- **Employer match tracking** - Track company contributions
- **IRS limit warnings** - Alert when approaching limits
- **Retirement goals** - Target amounts and projections
- **Enhanced reporting** - Contribution vs growth analysis

## Database Schema

### New Table: `retirement_contribution`

Track contributions separately from balance updates:

```python
class RetirementContribution(db.Model):
    __tablename__ = 'retirement_contributions'

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    contribution_date = db.Column(db.Date, nullable=False)
    employee_amount = db.Column(db.Numeric(15, 2), default=0)
    employer_match = db.Column(db.Numeric(15, 2), default=0)
    contribution_type = db.Column(
        db.Enum('regular', 'catchup', 'rollover'),
        default='regular'
    )
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    account = db.relationship('Account', backref='contributions')

    __table_args__ = (
        db.Index('idx_contribution_account_date', 'account_id', 'contribution_date'),
    )
```

### New Table: `retirement_goal`

Track retirement savings goals:

```python
class RetirementGoal(db.Model):
    __tablename__ = 'retirement_goals'

    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False)
    name = db.Column(db.String(128), nullable=False)  # e.g., "Retirement at 65"
    target_amount = db.Column(db.Numeric(15, 2), nullable=False)
    target_date = db.Column(db.Date, nullable=False)
    monthly_contribution_target = db.Column(db.Numeric(15, 2), nullable=True)
    expected_return_rate = db.Column(db.Numeric(5, 2), default=7.0)  # Annual %
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    family = db.relationship('Family', backref='retirement_goals')
```

## IRS Contribution Limits (2025)

Track and warn about limits:

```python
IRS_LIMITS_2025 = {
    'traditional_401k': {'regular': 23500, 'catchup': 7500},  # 50+ catchup
    'roth_401k': {'regular': 23500, 'catchup': 7500},
    'traditional_ira': {'regular': 7000, 'catchup': 1000},
    'roth_ira': {'regular': 7000, 'catchup': 1000},
    'sep_ira': {'regular': 69000, 'catchup': 0},
    '403b': {'regular': 23500, 'catchup': 7500},
}

def get_year_contributions(account, year):
    """Get total contributions for a year."""
    return db.session.query(
        func.sum(RetirementContribution.employee_amount)
    ).filter(
        RetirementContribution.account_id == account.id,
        extract('year', RetirementContribution.contribution_date) == year
    ).scalar() or 0

def check_contribution_limit(account, new_amount, year=None):
    """Check if contribution would exceed IRS limits."""
    year = year or datetime.now().year
    current = get_year_contributions(account, year)
    limit = IRS_LIMITS_2025.get(account.retirement_type, {}).get('regular', 0)

    remaining = limit - current
    if new_amount > remaining:
        return {
            'exceeded': True,
            'limit': limit,
            'current': current,
            'remaining': remaining,
            'overage': new_amount - remaining
        }
    return {'exceeded': False, 'remaining': remaining - new_amount}
```

## UI Changes

### Contribution Entry Form

Add to account detail page for retirement accounts:

```
Add Contribution
----------------
Date: [2025-12-15]
Your Contribution: [$500.00]
Employer Match: [$250.00]
Type: [Regular ▼]  (Regular, Catch-up, Rollover)
Notes: [Optional]

Year-to-Date: $18,500 of $23,500 limit (78%)
[████████████████████░░░░░]

[Save Contribution]
```

### Contribution History

Show on account detail page:

```
Contribution History
--------------------
Date         You        Employer   Type      Total
2025-12-01   $500.00    $250.00    Regular   $750.00
2025-11-01   $500.00    $250.00    Regular   $750.00
2025-10-01   $500.00    $250.00    Regular   $750.00
...

YTD Total: $6,000.00 + $3,000.00 match = $9,000.00
```

### Retirement Goals Page (`/retirement/goals`)

```
Retirement Goals
----------------
[+ Add Goal]

Goal: Retirement at 65
Target: $1,000,000 by 2045
Current Total: $83,930.50
Progress: [████████░░░░░░░░░░░░] 8.4%
Monthly Target: $1,200/month to reach goal

[Edit] [Delete]
```

### Enhanced Retirement Report

Expand `/reports/retirement`:

```
Retirement Summary
==================

Total Retirement Savings: $83,930.50

By Account:
- 401(k) - Employer Plan     $45,230.50  (54%)
- Traditional IRA            $23,100.00  (28%)
- Roth IRA                   $15,600.00  (18%)

2025 Contributions:
- Your Contributions:    $12,000.00
- Employer Matches:       $6,000.00
- Total:                 $18,000.00

Growth Analysis:
- Starting Balance (Jan 1):  $72,000.00
- Contributions:             $18,000.00
- Market Gains/Losses:       -$6,069.50
- Ending Balance:            $83,930.50
- Return Rate:               -7.2%

[Chart: Balance Over Time]
[Chart: Contributions vs Growth]
```

## Implementation Plan

### Phase 1: Contribution Tracking
- [ ] Create migration for `retirement_contributions` table
- [ ] Create `RetirementContribution` model
- [ ] Add contribution service with IRS limit checking
- [ ] Add contribution form to account detail page
- [ ] Display contribution history
- [ ] Add YTD contribution summary

### Phase 2: Retirement Goals
- [ ] Create migration for `retirement_goals` table
- [ ] Create `RetirementGoal` model
- [ ] Add goal CRUD routes
- [ ] Create goals management page
- [ ] Implement projection calculator
- [ ] Display progress on dashboard

### Phase 3: Enhanced Reporting
- [ ] Expand `/reports/retirement` page
- [ ] Add contribution vs growth calculation
- [ ] Add balance over time chart
- [ ] Add contribution summary by year
- [ ] Add account allocation pie chart

### Phase 4: Testing
- [ ] Model tests for contributions
- [ ] Model tests for goals
- [ ] IRS limit calculation tests
- [ ] Route tests for contribution CRUD
- [ ] Route tests for goal CRUD
- [ ] Projection calculator tests

## API Endpoints

```python
# Contributions
POST   /accounts/<id>/contributions      # Add contribution
GET    /accounts/<id>/contributions      # List contributions
PUT    /contributions/<id>               # Update contribution
DELETE /contributions/<id>               # Delete contribution

# Goals
GET    /retirement/goals                 # List goals
POST   /retirement/goals                 # Create goal
GET    /retirement/goals/<id>            # Get goal details
PUT    /retirement/goals/<id>            # Update goal
DELETE /retirement/goals/<id>            # Delete goal

# Reports
GET    /reports/retirement               # Retirement report
GET    /api/retirement/summary           # JSON summary for charts
```

## Security & Privacy

- All queries scoped by `family_id`
- Contribution data is sensitive financial information
- Goals are family-scoped (shared between family members)
- Audit logging for contribution changes

## Future Enhancements

- Tax bracket optimization suggestions
- Roth conversion analysis
- Required Minimum Distribution (RMD) calculator
- Social Security integration
- Monte Carlo retirement projections
- Asset allocation recommendations

---

## Dependencies

- **Depends On:** [account-management.md](account-management.md) - MUST be implemented first
- **Required By:** None (optional enhancement)
- **Related To:** Asset tracking (same balance history pattern)

## Open Questions

1. **Should contributions link to transactions?**
   - If user imports paycheck, link contribution to that transaction?
   - Answer: Nice to have, defer to v2

2. **Multiple goals per family?**
   - Different retirement dates for spouses?
   - Answer: Yes, support multiple goals

3. **Historical IRS limits?**
   - Track limits by year for accurate historical analysis?
   - Answer: Store limits in config, update annually
