# Development Setup

Set up a local development environment for FRacker.

## Prerequisites

- Python 3.10 or higher
- MySQL 8.0+ or MariaDB 10.5+
- Redis 6.0+
- Git

## Local Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/ahbergamo/finance_tracker.git
cd finance_tracker
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Database

Create a MySQL database:

```sql
CREATE DATABASE finance_tracker_dev;
CREATE USER 'finance_user'@'localhost' IDENTIFIED BY 'dev_password';
GRANT ALL PRIVILEGES ON finance_tracker_dev.* TO 'finance_user'@'localhost';
FLUSH PRIVILEGES;
```

### 5. Configure Environment

Create `.env` file:

```env
FLASK_CONFIG=config.config.DevelopmentConfig
SECRET_KEY=dev-secret-key-change-in-production
DB_USER=finance_user
DB_PASSWORD=dev_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=finance_tracker_dev
REDIS_URL=redis://localhost:6379
FLASK_DEBUG=True
```

### 6. Initialize Database

Run migrations:

```bash
flask db upgrade
```

Seed initial data:

```bash
flask seed-db
```

### 7. Start Development Server

```bash
python run.py
```

The application will be available at `http://localhost:5002`

## VS Code Development Container

For a consistent development environment, use the included Dev Container:

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [VS Code](https://code.visualstudio.com/)
- [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

### Setup

1. Open the project in VS Code
2. Press `F1` and select **Dev Containers: Reopen in Container**
3. Wait for the container to build and start
4. The development environment is ready to use!

The Dev Container includes:
- Python 3.11
- MySQL 8.0
- Redis 6.2
- All Python dependencies pre-installed
- Database pre-configured

## Running Tests

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=app --cov-report=html
```

View coverage report:

```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Run Specific Tests

```bash
# Run a specific test file
pytest tests/routes/test_auth.py

# Run tests matching a pattern
pytest -k "test_login"

# Run a specific test class
pytest tests/services/test_auth.py::TestAuthService
```

## Code Quality

### Linting

Run flake8 to check code style:

```bash
flake8 .
```

Configuration in `.flake8`:
- Max line length: 200
- Excludes: migrations, venv, __pycache__

### Format Code

The project follows PEP 8 style guidelines. Consider using:

```bash
# Auto-format with black (optional)
pip install black
black .
```

## Database Migrations

### Create a New Migration

After modifying models:

```bash
flask db migrate -m "Description of changes"
```

### Apply Migrations

```bash
flask db upgrade
```

### Rollback Migration

```bash
flask db downgrade
```

## Project Structure

```
finance_tracker/
├── app/                    # Main application package
│   ├── __init__.py        # App factory
│   ├── models/            # SQLAlchemy models
│   ├── routes/            # Flask blueprints
│   ├── services/          # Business logic
│   ├── forms/             # WTForms
│   ├── templates/         # Jinja2 templates
│   └── static/            # CSS, JS, images
├── config/                # Configuration classes
├── migrations/            # Alembic migrations
├── tests/                 # Test suite
├── run.py                 # Development entry point
└── requirements.txt       # Python dependencies
```

## Common Development Tasks

### Reset Database

```bash
# Drop and recreate
flask db downgrade base
flask db upgrade
flask seed-db
```

### Add a New Route

1. Create route file in `app/routes/`
2. Define blueprint and routes
3. Register blueprint in `app/__init__.py`
4. Add tests in `tests/routes/`

### Add a New Model

1. Create model in `app/models/`
2. Import in `app/models/__init__.py`
3. Create migration: `flask db migrate`
4. Apply migration: `flask db upgrade`
5. Add tests in `tests/models/`

### Debug in VS Code

Add breakpoints and use the included launch configuration:

Press `F5` or use **Run → Start Debugging**

## Useful Flask Commands

```bash
# List all routes
flask routes

# Open Flask shell
flask shell

# Run custom CLI command
flask seed-db
```

## Environment Variables

| Variable | Development Default | Description |
|----------|---------------------|-------------|
| `FLASK_CONFIG` | `DevelopmentConfig` | Configuration class |
| `FLASK_DEBUG` | `True` | Enable debug mode |
| `DB_HOST` | `localhost` | Database host |
| `DB_PORT` | `3306` | Database port |
| `REDIS_URL` | `redis://localhost:6379` | Redis connection |

## Troubleshooting

### Port Already in Use

Change the port in `run.py`:

```python
app.run(host='0.0.0.0', port=5003, debug=True)
```

### Database Connection Error

Ensure MySQL is running:

```bash
sudo systemctl status mysql  # Linux
brew services list  # macOS
```

### Redis Connection Error

Ensure Redis is running:

```bash
redis-cli ping  # Should return "PONG"
```

## Next Steps

- Review [Contributing Guidelines](../contributing.md)
- Check the [CLAUDE.md](https://github.com/ahbergamo/finance_tracker/blob/main/CLAUDE.md) file for codebase guidance
- Read about the [project structure](../index.md#features)
