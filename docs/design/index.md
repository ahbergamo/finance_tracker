# Design Documentation

This section contains design documents for features under development or planning.

## Purpose

Design documents help us:

- Plan implementations before writing code
- Document architectural decisions
- Gather feedback from contributors
- Maintain a record of design evolution

## Design Documents

### Implemented Features

- [Transaction Management](transaction-management.md) - Current transaction-based accounting system (✅ Implemented)

### In Review

- [Account Management](account-management.md) - Separate accounts from CSV templates, enable multiple accounts per type (🔵 In Review)

### Planned Enhancements

- [Retirement Accounts Enhancement](retirement-accounts.md) - Advanced retirement tracking with contribution goals and projections (🟡 Draft, depends on Account Management)
- [Asset Management](asset-management.md) - Track physical assets and net worth (🟡 Draft)

### Document Dependencies

```
transaction-management.md (✅ Implemented)
    ↓
account-management.md (🔵 In Review) ← We are here
    ↓
    ├─→ retirement-accounts.md (🟡 Draft)
    └─→ asset-management.md (🟡 Draft)
```

## Design Document Template

When creating a new design document, include:

### 1. Overview
- What problem does this solve?
- Who is it for?
- What are the key goals?

### 2. Requirements
- Functional requirements
- Non-functional requirements (performance, security, etc.)
- User stories

### 3. Proposed Solution
- High-level architecture
- Database schema changes
- API/interface design
- User interface mockups

### 4. Implementation Plan
- Phases or milestones
- Dependencies
- Testing strategy

### 5. Alternatives Considered
- What other approaches were evaluated?
- Why was this approach chosen?

### 6. Open Questions
- Unresolved design decisions
- Areas needing more research

## Contributing Design Documents

To propose a new feature:

1. Create a new design document in `docs/design/`
2. Follow the template above
3. Open a pull request for review
4. Discuss and iterate on the design
5. Implement once the design is approved

## Status Indicators

| Status | Meaning |
|--------|---------|
| 🟡 **Draft** | Initial proposal, under discussion |
| 🔵 **In Review** | Ready for feedback |
| 🟢 **Approved** | Ready for implementation |
| 🟣 **In Progress** | Currently being implemented |
| ✅ **Implemented** | Feature is live |
| ⛔ **Rejected** | Not moving forward |

---

*This design documentation process helps ensure well-thought-out features and maintains a record of architectural decisions for future reference.*
