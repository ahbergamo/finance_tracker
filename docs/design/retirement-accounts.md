# Retirement Accounts Enhancement

**Status:** Not Started (Future Feature)
**Created:** 2025-12-20
**Updated:** 2025-12-23
**Author:** FRacker Team
**Depends On:** [account-management.md](account-management.md) (Done)

## Overview

Enhance FRacker's retirement account tracking with contribution tracking, goal projections, and reporting. This builds upon the Account Management system which provides balance history tracking.

### Current State (from Account Management)

- Retirement accounts can be created with subtypes (traditional_401k, roth_401k, etc.)
- Balance snapshots tracked in `account_balance_history`
- Balance history UI at `/accounts/<id>/balances`
- Net worth report includes retirement accounts
- Basic retirement report exists at `/reports/retirement`

### Goals (This Enhancement)

- Track retirement contributions separately from market gains
- Record employer matches
- Warn when approaching IRS contribution limits
- Calculate progress toward retirement goals
- Visualize growth over time (contributions vs market gains)

### Non-Goals

- Real-time market data integration
- Automated brokerage imports
- Tax calculation or reporting
- Investment recommendations
- Individual holdings tracking

## Database Schema

### New Table: `retirement_contributions`

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
```

### New Table: `retirement_goals`

Track retirement savings goals:

```python
class RetirementGoal(db.Model):
    __tablename__ = 'retirement_goals'

    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey('family.id'), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    target_amount = db.Column(db.Numeric(15, 2), nullable=False)
    target_date = db.Column(db.Date, nullable=False)
    monthly_contribution_target = db.Column(db.Numeric(15, 2), nullable=True)
    expected_return_rate = db.Column(db.Numeric(5, 2), default=7.0)
    notes = db.Column(db.Text, nullable=True)
```

## IRS Contribution Limits (2025)

```python
IRS_LIMITS_2025 = {
    'traditional_401k': {'regular': 23500, 'catchup': 7500},
    'roth_401k': {'regular': 23500, 'catchup': 7500},
    'traditional_ira': {'regular': 7000, 'catchup': 1000},
    'roth_ira': {'regular': 7000, 'catchup': 1000},
    'sep_ira': {'regular': 69000, 'catchup': 0},
    '403b': {'regular': 23500, 'catchup': 7500},
}
```

## UI Mockups

### Contribution Entry Form

On retirement account detail page:

```
Add Contribution
----------------
Date: [2025-12-15]
Your Contribution: [$500.00]
Employer Match: [$250.00]
Type: [Regular v]  (Regular, Catch-up, Rollover)
Notes: [Optional]

Year-to-Date: $18,500 of $23,500 limit (78%)
[================----]

[Save Contribution]
```

### Enhanced Retirement Report

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

## Open Questions

1. **Should contributions link to transactions?**
   - If user imports paycheck, link contribution to that transaction?
   - Answer: Defer to v2

2. **Multiple goals per family?**
   - Different retirement dates for spouses?
   - Answer: Yes, support multiple goals

3. **Historical IRS limits?**
   - Track limits by year for accurate historical analysis?
   - Answer: Store limits in config, update annually
