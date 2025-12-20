# Quick Start Guide

Get FRacker up and running in minutes with Docker.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- 2GB+ RAM recommended
- Port 1310 available (or configure a different port)

## Installation Steps

### 1. Download FRacker

Download the latest release from GitHub:

```bash
git clone https://github.com/ahbergamo/finance_tracker.git
cd finance_tracker
```

Or download a specific release from the [Releases page](https://github.com/ahbergamo/finance_tracker/releases).

### 2. Configure Environment

Copy the default environment file and customize it:

```bash
cp .env_default .env
```

Edit `.env` with your preferred settings:

```env
# Application Settings
SECRET_KEY=your_super_secret_key_change_this
FLASK_CONFIG=config.config.PortableConfig

# Database Configuration
DB_USER=finance_user
DB_PASSWORD=your_secure_database_password
DB_HOST=db
DB_PORT=3306
DB_NAME=finance_tracker

# Redis Configuration
REDIS_URL=redis://redis:6379

# Application Port
APP_PORT=1310
```

!!! warning "Security"
    Always change the `SECRET_KEY` and `DB_PASSWORD` to unique, strong values. Never commit `.env` files to version control.

### 3. Start the Application

Launch all services with Docker Compose:

```bash
docker-compose up -d
```

This will start:
- **FRacker Application** (Flask/Gunicorn)
- **MySQL Database**
- **Redis** (for sessions)
- **Nginx** (reverse proxy)

### 4. Access FRacker

Open your browser and navigate to:

```
http://localhost:1310
```

Or use your server's IP address:

```
http://192.168.1.100:1310
```

### 5. Create Your Account

1. Click **Register** on the login page
2. Enter your details:
    - Username
    - Email
    - Password
    - Family name (for multi-user support)
3. Click **Create Account**

!!! tip "Family Accounts"
    Multiple users can share a family account. All family members will see combined financial data.

## Next Steps

Now that FRacker is running, you're ready to:

1. [Configure Account Types](configuration.md#account-types) for your bank's CSV format
2. [Import Transactions](../user-guide/importing-transactions.md) from your bank
3. [Set Up Categories](../user-guide/categories-budgets.md#categories) and budgets
4. [Create Import Rules](../user-guide/import-rules.md) for automatic categorization

## Troubleshooting

### Port Already in Use

If port 1310 is already in use, change it in `.env`:

```env
APP_PORT=8080  # Use a different port
```

Then restart:

```bash
docker-compose down
docker-compose up -d
```

### Database Connection Issues

Check that all containers are running:

```bash
docker-compose ps
```

View logs for errors:

```bash
docker-compose logs finance_tracker
docker-compose logs db
```

### Need More Help?

Please [open an issue](https://github.com/ahbergamo/finance_tracker/issues) or check the project's [GitHub discussions](https://github.com/ahbergamo/finance_tracker/discussions).
