# CLAUDE.md - FRacker Personal Finance Tracker

This file provides guidance for Claude Code when working with this codebase.

## Project Overview

FRacker is a self-hosted personal finance tracking web application built with Flask. It enables users to import bank transactions via CSV, categorize expenses, set budgets, and visualize financial data through an interactive dashboard. Supports multi-user families sharing finances.

**Version**: 1.1.0
**License**: MIT

## Tech Stack

- **Backend**: Flask 2.x, SQLAlchemy, Flask-Login, Flask-WTF
- **Database**: MySQL/MariaDB (production), SQLite (development/testing)
- **Sessions**: Redis
- **Server**: Gunicorn behind Nginx
- **Frontend**: Jinja2 templates, Bootstrap, Chart.js
- **Testing**: Pytest with coverage
- **Deployment**: Docker Compose

## Project Structure

```
finance_tracker/
├── app/                      # Main Flask application
│   ├── __init__.py          # App factory and blueprint registration
│   ├── cli.py               # CLI commands (flask seed-db)
│   ├── constants/           # Default values (account_types.py)
│   ├── forms/               # WTForms form definitions
│   ├── models/              # SQLAlchemy ORM models
│   ├── routes/              # Flask blueprints (route handlers)
│   │   ├── transactions/    # Transaction CRUD and import
│   │   └── reports/         # Financial reports (monthly, annual, etc.)
│   ├── services/            # Business logic layer
│   │   └── transactions/    # Transaction-related services
│   ├── templates/           # Jinja2 HTML templates
│   ├── static/              # CSS, JS, images
│   └── utils/               # Utility functions
├── config/config.py         # Environment configurations
├── migrations/              # Alembic database migrations
├── tests/                   # Pytest test suite
├── docker/                  # Production Docker setup
├── docker_portable/         # Portable Docker builds
├── .devcontainer/           # VS Code dev container
├── run.py                   # Flask entry point
└── requirements.txt         # Python dependencies
```

## Key Models

- **User**: Authentication, belongs to a Family
- **Family**: Groups users for shared financial data
- **Transaction**: Core financial record (amount, description, category, account)
- **Category**: Transaction categories, scoped to family
- **Budget**: Spending limits with many-to-many relationship to categories
- **Account**: Bank accounts with type (checking, savings, credit_card, retirement, brokerage), CSV field mappings, and initial balance
- **AccountBalanceHistory**: Balance snapshots for retirement/brokerage accounts (date + balance)
- **ImportRule**: Pattern-based auto-categorization during CSV import

## Common Commands

```bash
# Development
python run.py                    # Run Flask dev server
flask db upgrade                 # Apply database migrations
flask seed-db                    # Seed default data

# Testing
pytest                           # Run all tests with coverage
pytest tests/routes/test_auth.py # Run specific test file
pytest -k "test_login"           # Run tests matching pattern

# Linting
flake8 .                         # Check code style

# Docker
docker-compose up -d             # Start all services
docker-compose logs finance_tracker  # View app logs
docker-compose build --no-cache  # Rebuild after changes
```

## Environment Configuration

Key environment variables (see `.env`):
```
FLASK_CONFIG=config.config.DevelopmentConfig  # or PortableConfig, ProductionConfig
SECRET_KEY=your_secure_key
DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME  # MySQL connection
REDIS_URL=redis://localhost:6379
```

## Architecture Patterns

1. **Blueprints**: Routes organized by feature (auth, transactions, budgets, reports)
2. **Service Layer**: Business logic in `app/services/`, called by routes
3. **Family Scoping**: All data queries filter by `current_user.family_id`
4. **Flask-Login**: `@login_required` decorator on protected routes

## Key Routes

| Path | Purpose |
|------|---------|
| `/` | Redirects to dashboard or login |
| `/auth/login`, `/auth/register` | Authentication |
| `/dashboard` | Main dashboard with charts |
| `/transactions` | List, filter, add, edit, delete transactions |
| `/transactions/import` | CSV import with preview |
| `/budgets` | Budget management |
| `/categories` | Category management |
| `/account_types` | Account management (checking, savings, credit card, retirement, brokerage) |
| `/accounts/<id>/balances` | Balance history for retirement/brokerage accounts |
| `/import-rules` | Auto-categorization rules |
| `/reports/*` | Monthly, annual, income/expense, retirement, net worth reports |

## CSV Import Flow

1. User uploads CSV file
2. System parses using AccountType field mappings
3. ImportRules apply auto-categorization
4. Duplicate detection (file and database)
5. Preview shown to user
6. User confirms import

## Testing

- Uses in-memory SQLite for speed
- CSRF disabled in test config
- Fixtures in `tests/conftest.py`
- Test data seeded via `tests/seed_test_data.py`

## Git Workflow

- **main**: Stable production releases
- **develop**: Integration branch (PRs target here)
- **feature/***: Feature development branches

## Important Conventions

- All timestamps stored in UTC
- Password hashing via Werkzeug
- CSRF protection enabled on all forms
- Family-scoped queries prevent cross-user data access
- Logging to `logs/finance_tracker.log` in production
