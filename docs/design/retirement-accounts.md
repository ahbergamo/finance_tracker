# Retirement Accounts Design

**Status:** 🟡 Draft
**Created:** 2025-12-20
**Author:** FRacker Team

## Overview

Add comprehensive retirement and investment account tracking to FRacker, enabling users to monitor 401(k), IRA, and other long-term savings accounts alongside their regular transactions.

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

## Current State

FRacker currently has:
- `/reports/retirement` route (partially implemented)
- Retirement categories in the default category list
- Basic retirement account types

Missing:
- Balance tracking over time
- Dedicated retirement account management UI
- Historical balance data
- Asset allocation tracking

## Proposed Solution

### Database Schema Changes

#### New Table: `retirement_balance`

Tracks balance snapshots over time:

```sql
CREATE TABLE retirement_balance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_id INT NOT NULL,  -- FK to account_type or new retirement_account table
    user_id INT NOT NULL,     -- FK to user
    balance DECIMAL(15, 2) NOT NULL,
    as_of_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES account_type(id),
    FOREIGN KEY (user_id) REFERENCES user(id),
    UNIQUE KEY unique_balance (account_id, as_of_date)
);
```

#### Alternative: Extend `account_type` table

Add retirement-specific fields:

```sql
ALTER TABLE account_type ADD COLUMN is_retirement BOOLEAN DEFAULT FALSE;
ALTER TABLE account_type ADD COLUMN current_balance DECIMAL(15, 2);
ALTER TABLE account_type ADD COLUMN last_balance_update DATE;
```

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

### Phase 1: Data Model (Week 1)
- [ ] Create `retirement_balance` table migration
- [ ] Create `RetirementBalance` model
- [ ] Add model tests
- [ ] Seed sample data for testing

### Phase 2: Backend Services (Week 2)
- [ ] Create retirement service layer
- [ ] Implement balance CRUD operations
- [ ] Add balance history queries
- [ ] Create API endpoints
- [ ] Add service tests

### Phase 3: User Interface (Week 3)
- [ ] Create retirement accounts list page
- [ ] Add balance update form
- [ ] Implement balance history charts
- [ ] Enhanced retirement report page
- [ ] Add navigation links

### Phase 4: Testing & Polish (Week 4)
- [ ] Integration tests
- [ ] UI/UX refinements
- [ ] Documentation updates
- [ ] Performance optimization

## Alternatives Considered

### Option 1: Use Transactions for Balances
**Approach:** Store balances as special transaction types
**Pros:** Reuses existing infrastructure
**Cons:** Transactions are flow-based, not balance-based; confusing semantics
**Decision:** Rejected - balances are fundamentally different from transactions

### Option 2: External Service Integration
**Approach:** Integrate with Plaid or similar for automatic balance updates
**Pros:** Automated, always current
**Cons:** External dependency, privacy concerns, cost, complexity
**Decision:** Deferred - manual entry for v1, consider for future enhancement

### Option 3: Full Investment Tracking
**Approach:** Track individual holdings, shares, cost basis
**Pros:** Complete portfolio management
**Cons:** Significant complexity, scope creep
**Decision:** Out of scope - focus on balance tracking first

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
