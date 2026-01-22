# Deployment Guide

This guide will help you deploy ImageOptimizer to production.

## Prerequisites

- Server with Python 3.12+ installed
- PostgreSQL or MySQL database (recommended for production)
- Web server (Nginx or Apache)
- SSL certificate (Let's Encrypt recommended)
- Google OAuth credentials

## Step-by-Step Deployment

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib
```

### 2. Create Database

```bash
# Login to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE imageoptimizer;
CREATE USER imageoptimizer_user WITH PASSWORD 'your_strong_password';
ALTER ROLE imageoptimizer_user SET client_encoding TO 'utf8';
ALTER ROLE imageoptimizer_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE imageoptimizer_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE imageoptimizer TO imageoptimizer_user;
\q
```

### 3. Clone and Setup Application

```bash
# Create application directory
sudo mkdir -p /var/www/imageoptimizer
sudo chown $USER:$USER /var/www/imageoptimizer
cd /var/www/imageoptimizer

# Clone repository
git clone https://github.com/tiholic/ImageOptimizer.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install psycopg2-binary gunicorn
```

### 4. Configure Environment

```bash
# Create .env file
cp .env.example .env

# Edit .env file
nano .env
```

Set the following in your `.env` file:

```env
SECRET_KEY=your_generated_secret_key_here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DATABASE_URL=postgres://imageoptimizer_user:your_strong_password@localhost:5432/imageoptimizer

# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Storage Encryption
STORAGE_ENCRYPTION_KEY=your_generated_encryption_key_here

# CORS (if needed)
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 5. Update Django Settings for Production

Update `imageoptimizer/settings.py` to support PostgreSQL:

```python
import dj_database_url

# Database
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600
    )
}
```

### 6. Collect Static Files and Migrate

```bash
# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

### 7. Configure Gunicorn

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/imageoptimizer.service
```

Add the following content:

```ini
[Unit]
Description=ImageOptimizer Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/imageoptimizer
EnvironmentFile=/var/www/imageoptimizer/.env
ExecStart=/var/www/imageoptimizer/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/var/www/imageoptimizer/imageoptimizer.sock \
          imageoptimizer.wsgi:application

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl start imageoptimizer
sudo systemctl enable imageoptimizer
sudo systemctl status imageoptimizer
```

### 8. Configure Nginx

Create Nginx configuration:

```bash
sudo nano /etc/nginx/sites-available/imageoptimizer
```

Add the following content:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    client_max_body_size 50M;

    location /static/ {
        alias /var/www/imageoptimizer/staticfiles/;
    }

    location /media/ {
        alias /var/www/imageoptimizer/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/imageoptimizer/imageoptimizer.sock;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/imageoptimizer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 9. Setup SSL with Let's Encrypt

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Certbot will automatically update the Nginx configuration
```

### 10. Configure Google OAuth Redirect URIs

In Google Cloud Console, update the authorized redirect URIs to:

```
https://yourdomain.com/accounts/google/login/callback/
```

## Security Checklist

- [ ] Set `DEBUG=False` in production
- [ ] Use a strong `SECRET_KEY`
- [ ] Use HTTPS (SSL certificate)
- [ ] Configure `ALLOWED_HOSTS` properly
- [ ] Use a production database (PostgreSQL/MySQL)
- [ ] Enable firewall (UFW)
- [ ] Configure backup strategy
- [ ] Set up monitoring and logging
- [ ] Regularly update dependencies
- [ ] Use environment variables for sensitive data

## Monitoring

### Application Logs

```bash
# View Gunicorn logs
sudo journalctl -u imageoptimizer -f

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Database Backups

Set up automated PostgreSQL backups:

```bash
# Create backup script
nano /usr/local/bin/backup-imageoptimizer.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/imageoptimizer"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
pg_dump imageoptimizer > $BACKUP_DIR/imageoptimizer_$DATE.sql
# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
```

```bash
# Make executable
chmod +x /usr/local/bin/backup-imageoptimizer.sh

# Add to crontab (daily at 2 AM)
sudo crontab -e
0 2 * * * /usr/local/bin/backup-imageoptimizer.sh
```

## Scaling

### Horizontal Scaling

For high traffic, consider:

1. **Load Balancer**: Use AWS ELB, Nginx, or HAProxy
2. **Multiple App Servers**: Run multiple Gunicorn instances
3. **Separate Database Server**: Move PostgreSQL to dedicated server
4. **CDN**: Use CloudFront or CloudFlare for static files
5. **Caching**: Add Redis for session and query caching

### Vertical Scaling

- Increase server resources (CPU, RAM)
- Optimize database queries
- Add database indexes
- Use database read replicas

## Maintenance

### Update Application

```bash
cd /var/www/imageoptimizer
source venv/bin/activate

# Pull latest changes
git pull

# Install new dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart service
sudo systemctl restart imageoptimizer
```

## Troubleshooting

### Common Issues

1. **Static files not loading**
   - Run `python manage.py collectstatic`
   - Check Nginx configuration

2. **Database connection errors**
   - Check DATABASE_URL in .env
   - Verify PostgreSQL is running

3. **502 Bad Gateway**
   - Check Gunicorn service status
   - Review application logs

4. **Permission errors**
   - Check file ownership
   - Verify socket file permissions

## Support

For issues and questions:
- GitHub Issues: https://github.com/tiholic/ImageOptimizer/issues
- Documentation: See README.md and API_DOCUMENTATION.md
