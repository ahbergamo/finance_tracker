# Contributing to FRacker

Thank you for your interest in contributing to this project!

This guide will walk you through how to get set up and start contributing, whether it’s code, documentation, bug reports, or feature ideas.

---

## Local Development Setup

### Prerequisites

- [Docker](https://www.docker.com/)
- [Visual Studio Code](https://code.visualstudio.com/)
- VS Code extensions:
  - Remote - Containers
  - Docker

### Dev Container Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/ahbergamo/finance-tracker.git
   cd finance-tracker
   ```

2. Open the project in VS Code and **reopen in container** when prompted.

The dev container includes:

- Hot-reloading Flask server
- Flake8 linting
- pytest
- Python dependencies installed via `requirements.txt`

---

## Deployment Options

FRacker can be run in three main ways:

### 1. Run Locally in VS Code (Dev Container)
- Launch using the built-in Flask server via VS Code.
- Great for debugging and development.

### 2. Deploy to Raspberry Pi or LAN Server
Use the `docker/` directory and `deploy_pi.sh` script to deploy to a Pi or other host:

```bash
docker/deploy_pi.sh
```

This runs the full stack using Docker Compose with your configured `.env`.

### 3. Deploy to Docker Hub for Cross-Platform Use
Build and push portable images using `docker_portable/` and:

```bash
docker_portable/deploy_linux.sh
```

This produces multi-arch builds and publishes them to Docker Hub for wide use.

---

To prepare your `.env` file:

```bash
cp .env_default .env
```

Make any required edits, then deploy using one of the options above.

---

## Testing & Linting

- **Lint your code**:

  ```bash
  flake8 .
  ```

- **Run tests**:

  ```bash
  pytest .
  ```

- **Seed the database** (optional):

  > A CLI command `flask seed_db` is included for development convenience if `app/cli.py` exists. It is primarily used by maintainers to pre-populate data during testing and is **not required** for general development.


  Create app/cli.py with seed data. Then call it from your shell:
  ```bash
  flask seed-db
  ````

- **Database migration**:

  ```bash
  flask db migrate && flask db upgrade
  ```

---

## CI/CD

This project uses GitHub Actions to automate testing, Docker builds, and release tagging:

- All PRs and pushes to `main`, `develop`, `feature/**`, or `release/**` run:

  - Lint checks via `flake8`
  - Unit tests via `pytest`
  - Coverage reports are uploaded as artifacts

- On merging a `release/x.y.z` branch into `main`:

  - A Git tag (e.g., `v1.2.0`) is created
  - A `.tar.gz` archive of release artifacts is uploaded
  - A GitHub Release is published automatically

- On push to `main`, Docker images are built and pushed for:

  - `linux/amd64` and `linux/arm64` platforms
  - App (`latest` and `${APP_VERSION}` tags)
  - Nginx (`nginx` and `nginx-${APP_VERSION}` tags)

---

## Code Guidelines

Before submitting a PR:

- Format your code using `Black` or ensure it passes `flake8`
- Add or update **docstrings** and **comments** where helpful
- Keep changes focused (one feature or fix per PR)
- Include or update related tests if applicable
- Update documentation if needed (README or this file)

### Before You Commit Checklist

- [x] Code passes `flake8` (or is autoformatted)
- [x] All tests pass (run `pytest`)
- [x] No secrets, tokens, or credentials are committed
- [x] Docs are updated if applicable

---

## Versioning

We use [Semantic Versioning](https://semver.org/) for all tagged releases:

- `MAJOR` (x): Incompatible changes or breaking API revisions
- `MINOR` (y): Backward-compatible feature additions
- `PATCH` (z): Backward-compatible bug fixes

Example: `1.2.3` = Major version 1, Minor release 2, Patch 3

---

## Branching Strategy

We follow a simplified Git flow:

- `main` → Production-ready code only, tagged releases
- `develop` → Active development branch
- `feature/*` → New features (branch from and merge into `develop`)
- `release/*` → Staging/testing branches (branch from `develop`, merge into `main`)
- `hotfix/*` → Emergency fixes from `main` (merge into `main` and `develop`)

### Example Branch Names

- `feature/user-auth`
- `release/1.2.0`
- `hotfix/fix-login-redirect`

### Release Workflow

1. Code is developed and tested in `develop`
2. A `release/x.y.z` branch is created and finalized
3. A PR is opened to merge the `release/x.y.z` into `main`
4. When merged:
   - A Git tag (`v1.2.0`) is created automatically
   - A GitHub Release is published with artifacts from `docker_portable/Dist/`
   - The `release/x.y.z` branch is automatically deleted
5. Optionally, `main` is merged back into `develop` to sync changes

> Need a refresher? [What is Git Flow?](https://nvie.com/posts/a-successful-git-branching-model/)

---

## Submitting a Pull Request

1. Fork the repo and create a feature branch:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Push to your fork:

   ```bash
   git push origin feature/your-feature-name
   ```

3. Open a Pull Request on GitHub against the `develop` branch.

4. Describe your changes clearly and link any related issues.

---

## Got Questions?

Feel free to open a [Discussion](https://github.com/ahbergamo/finance-tracker/discussions) or create an [Issue](https://github.com/ahbergamo/finance_tracker/issues) for help, suggestions, or clarifications.

Thank you.