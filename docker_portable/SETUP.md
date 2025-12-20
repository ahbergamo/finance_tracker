# Finance Tracker - Raspberry Pi Setup

## Before First Deployment

1. **Create your .env file** from the template:
   ```bash
   cp docker_portable/release/env_default docker_portable/.env
   ```

2. **Edit docker_portable/.env** and update these values:

   ```bash
   # REQUIRED - Generate a secure secret key (use: python -c "import secrets; print(secrets.token_hex(32))")
   SECRET_KEY=your-generated-secret-key-here

   # REQUIRED - Set a strong MySQL password
   DB_PASSWORD=your-strong-database-password

   # Optional - Change if needed
   DB_USER=finance_user        # Can keep default
   DB_PORT=3306                 # Can keep default
   DB_NAME=finance_tracker      # Can keep default
   ```

3. **Deploy to your Raspberry Pi**:
   ```bash
   ./deploy_pi_local.sh
   ```

## What This Does

- Creates a self-contained deployment with:
  - Flask app (finance_tracker)
  - MariaDB database (ARM-compatible)
  - Redis for sessions
  - Nginx reverse proxy
- All data stored in Docker volumes (persists between deployments)
- Accessible on port 1310

## First Time Setup on Pi

After deployment, the database will be created automatically. The app will be available at:
- http://your-pi-ip:1310

## Troubleshooting

- If containers fail to start, check logs: `docker logs finance_tracker_portable`
- Database issues: `docker logs mysql_db`
- Make sure Docker is installed: `docker --version`