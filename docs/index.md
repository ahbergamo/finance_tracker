# FRacker - Your Personal Financial tRacker

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/ahbergamo/finance_tracker/blob/main/LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/ahbergamo/finance_tracker)](https://github.com/ahbergamo/finance_tracker)
[![Docker Pulls](https://img.shields.io/docker/pulls/abergamo/finance-tracker)](https://hub.docker.com/r/abergamo/finance-tracker)

A self-hosted personal finance tracking web application built with Flask.

<figure markdown>
  ![Dashboard Screenshot](assets/screenshots/Dashboard.png){ width="600" }
  <figcaption>Interactive dashboard with customizable charts</figcaption>
</figure>

Track expenses, categorize transactions, set budgets, and visualize your financial data—all securely hosted on your own server or Raspberry Pi.

---

## Features

- **📊 Interactive Dashboard** - Customizable charts powered by Chart.js
- **💳 CSV Import** - Import bank transactions from any institution
- **🏷️ Smart Categorization** - Automatic categorization with import rules
- **💰 Budget Tracking** - Set and monitor monthly budgets per category
- **👨‍👩‍👧‍👦 Multi-User Support** - Family accounts with shared finances
- **🔒 Secure** - Password hashing, CSRF protection, Redis sessions
- **🐳 Easy Deployment** - Docker support for Linux, Windows, and Raspberry Pi
- **📈 Comprehensive Reports** - Monthly, annual, and custom date range reports

---

## Quick Start

Get started with FRacker in under 5 minutes using Docker:

```bash
# Download the latest release
git clone https://github.com/ahbergamo/finance_tracker.git
cd finance_tracker

# Configure environment
cp .env_default .env
# Edit .env with your preferred settings

# Start the application
docker-compose up -d
```

The app will be available at [http://localhost:1310](http://localhost:1310)

!!! tip "First Steps"
    1. Create an account and family
    2. Set up account types for your bank's CSV format
    3. Import your first transactions
    4. Create categories and budgets

[Get Started →](getting-started/quick-start.md){ .md-button .md-button--primary }

---

## Screenshots

### Dashboard Overview
<figure markdown>
  ![Dashboard](assets/screenshots/Dashboard.png){ width="500" }
  <figcaption>Real-time financial overview with income/expense charts</figcaption>
</figure>

### Import Preview
<figure markdown>
  ![Import Preview](assets/screenshots/Import_Preview.png){ width="500" }
  <figcaption>Preview and validate transactions before importing</figcaption>
</figure>

### Import Rules
<figure markdown>
  ![Import Rules](assets/screenshots/Import_Rules.png){ width="500" }
  <figcaption>Automate categorization with pattern-based rules</figcaption>
</figure>

### Monthly Reports
<figure markdown>
  ![Monthly Report](assets/screenshots/Monthly_Report.png){ width="500" }
  <figcaption>Detailed spending analysis and trends</figcaption>
</figure>

---

## Why FRacker?

### Privacy First
Your financial data stays on **your** server. No third-party tracking, no data mining, no cloud dependencies.

### Open Source
MIT licensed. Review the code, contribute improvements, or fork for your own needs.

### Flexible
Works on any platform that supports Docker: desktop, server, or Raspberry Pi.

### Family-Friendly
Multiple users can share a family account with combined financial tracking.

---

## Support & Community

- **📖 Documentation**: You're reading it!
- **🐛 Bug Reports**: [GitHub Issues](https://github.com/ahbergamo/finance_tracker/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/ahbergamo/finance_tracker/discussions)
- **🤝 Contributing**: See our [Contributing Guide](contributing.md)

---

## License

FRacker is licensed under the [MIT License](https://github.com/ahbergamo/finance_tracker/blob/main/LICENSE).

---

!!! warning "Disclaimer"
    FRacker is a personal finance tracker intended for individual use. It is **not** a substitute for professional financial advice or accounting software.
