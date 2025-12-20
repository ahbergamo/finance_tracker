# Raspberry Pi Deployment

Run FRacker on your Raspberry Pi for a low-cost, self-hosted personal finance solution.

## Supported Models

- Raspberry Pi 4 (2GB+ RAM recommended)
- Raspberry Pi 3B+
- Raspberry Pi 5

!!! tip "Performance"
    For best performance, use a Raspberry Pi 4 with 4GB+ RAM and run from an SSD instead of SD card.

## Prerequisites

### 1. Operating System

Install **Raspberry Pi OS (64-bit)** Lite or Desktop:

- Download from [raspberrypi.com/software](https://www.raspberrypi.com/software/)
- Flash to SD card using Raspberry Pi Imager
- Enable SSH during setup for headless operation

### 2. Install Docker

SSH into your Pi and install Docker:

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

Log out and back in for group changes to take effect.

Install Docker Compose:

```bash
sudo apt update
sudo apt install docker-compose -y
```

Verify installation:

```bash
docker --version
docker-compose --version
```

## Installation

### 1. Download FRacker

```bash
cd ~
git clone https://github.com/ahbergamo/finance_tracker.git
cd finance_tracker
```

### 2. Configure Environment

```bash
cp .env_default .env
nano .env  # Or use vim/vi
```

Recommended settings for Raspberry Pi:

```env
SECRET_KEY=your_super_secret_key_change_this
FLASK_CONFIG=config.config.PortableConfig

DB_USER=finance_user
DB_PASSWORD=your_secure_password
DB_HOST=db
DB_PORT=3306
DB_NAME=finance_tracker

REDIS_URL=redis://redis:6379
APP_PORT=1310
```

### 3. Pull Docker Images

FRacker provides pre-built ARM64 images:

```bash
docker-compose pull
```

### 4. Start Services

```bash
docker-compose up -d
```

### 5. Verify Deployment

Check container status:

```bash
docker-compose ps
```

View logs:

```bash
docker-compose logs -f finance_tracker
```

Access FRacker at:

```
http://<raspberry-pi-ip>:1310
```

## Performance Optimization

### Use External Storage

For better performance, run the database on an external SSD:

1. Mount SSD to `/mnt/finance_data`
2. Update `docker-compose.yml` volume paths
3. Move MySQL data directory

### Limit Memory Usage

If using a Pi with limited RAM, add memory limits to `docker-compose.yml`:

```yaml
services:
  finance_tracker:
    mem_limit: 512m
  db:
    mem_limit: 256m
  redis:
    mem_limit: 128m
```

### Enable Swap

Increase swap space for stability:

```bash
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Set CONF_SWAPSIZE=2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

## Auto-Start on Boot

Enable Docker to start on boot:

```bash
sudo systemctl enable docker
```

FRacker containers will auto-start with Docker.

## Backup Strategy

Create automated backups of your database:

```bash
# Create backup script
cat > ~/backup-finance.sh << 'EOF'
#!/bin/bash
BACKUP_DIR=~/finance_backups
mkdir -p $BACKUP_DIR
DATE=$(date +%Y%m%d_%H%M%S)
docker exec finance_tracker_db mysqldump -u finance_user -p<password> finance_tracker > $BACKUP_DIR/backup_$DATE.sql
# Keep only last 30 days
find $BACKUP_DIR -name "backup_*.sql" -mtime +30 -delete
EOF

chmod +x ~/backup-finance.sh
```

Add to crontab for daily backups:

```bash
crontab -e
# Add: 0 2 * * * /home/pi/backup-finance.sh
```

## Monitoring

Monitor your Pi's temperature and performance:

```bash
# Check temperature
vcgencmd measure_temp

# Monitor resources
htop

# Check Docker stats
docker stats
```

## Troubleshooting

### Out of Memory

If the Pi runs out of memory:

1. Increase swap space (see above)
2. Add memory limits to containers
3. Consider upgrading to a Pi with more RAM

### Slow Performance

- Use SSD instead of SD card
- Reduce concurrent database connections
- Enable query caching in MySQL

### Network Issues

Ensure port 1310 is accessible:

```bash
sudo ufw allow 1310/tcp  # If using UFW firewall
```

## Security Recommendations

- Change default passwords
- Enable HTTPS with Let's Encrypt and Certbot
- Keep Raspberry Pi OS updated: `sudo apt update && sudo apt upgrade`
- Use a firewall: `sudo apt install ufw && sudo ufw enable`

## Next Steps

- [Configure Account Types](configuration.md#account-types)
- [Import Your First Transactions](../user-guide/importing-transactions.md)
- Set up HTTPS with Let's Encrypt for secure remote access
