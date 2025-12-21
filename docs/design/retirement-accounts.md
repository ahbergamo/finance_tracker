# Retirement Accounts Enhancement

**Status:** 🟡 Draft
**Created:** 2025-12-20
**Updated:** 2025-12-20
**Author:** FRacker Team
**Depends On:** [account-management.md](account-management.md)

## Overview

Enhance FRacker's retirement account tracking with advanced features like contribution tracking, goal projections, and asset allocation. This builds upon the Account Management system to provide retirement-specific functionality.

### Goals

- Track retirement account balances over time
- Record contributions and withdrawals
- Visualize growth and allocation
- Support multiple retirement account types
- Calculate progress toward retirement goals

### Non-Goals (for initial implementation)

- Real-time market data integration
- Automated brokerage imports
- Tax calculation or reporting
- Investment recommendations

## User Stories

1. As a user, I want to track my 401(k) balance so I can see my retirement savings grow
2. As a user, I want to record contributions and employer matches
3. As a user, I want to see charts of my retirement account balances over time
4. As a user, I want to track multiple retirement accounts (401k, Traditional IRA, Roth IRA)
5. As a user, I want to see my total net worth including retirement accounts

## Prerequisites

This feature **requires** the Account Management system to be implemented first (see [account-management.md](account-management.md)). Key prerequisites:

- `account` table with `account_category='retirement'`
- `account_balance_history` table for balance snapshots
- Account creation and balance update UI

## Current State (Post-Account Management)

What will exist after Account Management is implemented:
- Users can create retirement accounts (401k, IRA, Roth IRA, etc.)
- `account_balance_history` table tracks balance updates
- `/accounts/<id>` page shows balance history
- `/reports/retirement` route (partially implemented)

What this enhancement adds:
- Contribution tracking (separate from market gains)
- Employer match tracking
- Contribution limit warnings (IRS limits)
- Retirement goal projections
- Asset allocation visualization
- Enhanced retirement report page

## Proposed Solution

### Database Schema Changes

#### New Table: `retirement_contribution`

Track contributions separately from balance updates:

```sql
CREATE TABLE retirement_contribution (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_id INT NOT NULL,                             -- FK to account (must be category='retirement')
    contribution_date DATE NOT NULL,
    employee_contribution DECIMAL(15, 2) DEFAULT 0.00,   -- Employee contribution
    employer_match DECIMAL(15, 2) DEFAULT 0.00,          -- Employer match
    contribution_type ENUM('regular', 'catchup', 'rollover') DEFAULT 'regular',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES account(id) ON DELETE CASCADE,
    INDEX idx_account_date (account_id, contribution_date)
);
```

#### New Table: `retirement_goal`

Track retirement savings goals:

```sql
CREATE TABLE retirement_goal (
    id INT AUTO_INCREMENT PRIMARY KEY,
    family_id INT NOT NULL,
    target_amount DECIMAL(15, 2) NOT NULL,               -- Goal amount
    target_date DATE NOT NULL,                           -- Target retirement date
    monthly_contribution_goal DECIMAL(15, 2),            -- Suggested monthly contribution
    expected_return_rate DECIMAL(5, 2),                  -- Expected annual return (%)
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (family_id) REFERENCES family(id) ON DELETE CASCADE
);
```

**Note:** The `account_balance_history` table from Account Management is used for balance tracking, not a separate `retirement_balance` table.

### User Interface

#### New Page: `/retirement/accounts`

List of retirement accounts with current balances:

```
Retirement Accounts
-------------------
[+ Add Account]

401(k) - Employer Plan          $45,230.50  ↑ 12.3%
Traditional IRA - Vanguard      $23,100.00  ↑ 8.5%
Roth IRA - Fidelity            $15,600.00  ↑ 15.2%
-------------------------------------------
Total Retirement Savings:       $83,930.50
```

#### Balance Update Form

```
Update Balance
--------------
Account: [401(k) - Employer Plan ▼]
Balance: [$_________]
As of Date: [YYYY-MM-DD]
Notes: [Optional notes]

[Save Balance]
```

#### Enhanced Retirement Report

Expand `/reports/retirement` to show:
- Current balances
- Balance history chart
- Contribution tracking
- Year-over-year growth
- Projected retirement value (optional future enhancement)

### API Endpoints

```python
# List retirement accounts
GET /api/retirement/accounts

# Add/update balance
POST /api/retirement/balance
{
    "account_id": 1,
    "balance": 45230.50,
    "as_of_date": "2025-12-20"
}

# Get balance history
GET /api/retirement/balance/<account_id>?start_date=2024-01-01&end_date=2025-12-20

# Delete balance entry
DELETE /api/retirement/balance/<id>
```

## Implementation Plan

**Note:** This implementation assumes Account Management is complete.

### Phase 1: Contribution Tracking
- [ ] Create `retirement_contribution` table migration
- [ ] Create `RetirementContribution` model
- [ ] Add contribution CRUD operations
- [ ] Create contribution entry form
- [ ] Link contributions to transactions (optional)
- [ ] Add model and service tests

### Phase 2: Retirement Goals
- [ ] Create `retirement_goal` table migration
- [ ] Create `RetirementGoal` model
- [ ] Add goal management UI
- [ ] Implement projection calculator
- [ ] Add progress tracking
- [ ] Add goal tests

### Phase 3: Enhanced Reporting
- [ ] Expand `/reports/retirement` page
- [ ] Add contribution vs balance growth chart
- [ ] Implement asset allocation tracking (future)
- [ ] Add year-to-date contribution summary
- [ ] IRS contribution limit warnings

### Phase 4: Testing & Polish
- [ ] Integration tests for contribution tracking
- [ ] Goal projection accuracy tests
- [ ] UI/UX refinements
- [ ] Documentation updates
- [ ] Performance optimization

## Dependencies

- **Depends On:** [account-management.md](account-management.md) - MUST be implemented first
- **Required By:** None (optional enhancement)
- **Related To:** [asset-management.md](asset-management.md) - Net worth calculation

## Alternatives Considered

### Option 1: Separate Retirement Balance Table
**Approach:** Create `retirement_balance` table separate from `account_balance_history`
**Pros:** Retirement-specific schema
**Cons:** Duplication, Account Management already provides this
**Decision:** Rejected - use `account_balance_history` from Account Management

### Option 2: External Service Integration
**Approach:** Integrate with Plaid or similar for automatic balance updates
**Pros:** Automated, always current
**Cons:** External dependency, privacy concerns, cost, complexity
**Decision:** Deferred - manual entry for v1, consider for future enhancement

### Option 3: Full Investment Tracking
**Approach:** Track individual holdings, shares, cost basis
**Pros:** Complete portfolio management
**Cons:** Significant complexity, scope creep
**Decision:** Out of scope - focus on balance and contribution tracking first

## Open Questions

1. **Should we track asset allocation?**
   - e.g., 60% stocks, 30% bonds, 10% cash
   - Answer: Nice to have, but defer to v2

2. **How to handle employer matching?**
   - Track separately or combined with contributions?
   - Answer: Combined for simplicity, can separate in reports

3. **Support for non-retirement investment accounts?**
   - Brokerage accounts, crypto, etc.
   - Answer: Yes, but use same infrastructure (rename to "Investment Accounts"?)

4. **Historical data import?**
   - Allow bulk import of past balances?
   - Answer: Yes, provide CSV import for balance history

5. **Integration with existing transactions?**
   - Link contribution transactions to balance updates?
   - Answer: Optional - show related transactions in balance details

## Security & Privacy Considerations

- Balance data is sensitive - ensure family-scoped access control
- No automatic external connections (user privacy)
- Audit log for balance changes
- Secure storage of balance history

## Performance Considerations

- Index on `(account_id, as_of_date)` for fast balance lookups
- Limit chart data points for performance (monthly snapshots for >1 year views)
- Cache current balances

## Testing Strategy

- Unit tests for models and services
- Integration tests for API endpoints
- UI tests for critical user flows
- Test data generation for various scenarios
- Performance tests for large balance histories

## Documentation Updates Needed

- User guide: "Managing Retirement Accounts"
- Admin guide: "Retirement Account Configuration"
- API documentation
- Changelog entry

## Future Enhancements

- Retirement goal tracking and projections
- Asset allocation visualization
- Contribution limit tracking (IRS limits)
- Tax-advantaged account reporting
- Integration with tax software export

---

## Feedback & Discussion

Please provide feedback on this design by commenting on the related GitHub issue or pull request.

**Questions to consider:**
- Is the scope appropriate for v1?
- Are there critical features missing?
- Should we prioritize differently?
- Any technical concerns with the proposed approach?
