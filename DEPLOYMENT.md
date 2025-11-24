# Multibliz POS System - Deployment Guide

## 🚀 Quick Start (Development)

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   # Copy .env.example to .env
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Database Setup**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

4. **Collect Static Files**
   ```bash
   python manage.py collectstatic --noinput
   ```

5. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

## 📦 Production Deployment

### Pre-Deployment Checklist

- [ ] Set `DEBUG=False` in .env
- [ ] Generate and set unique `SECRET_KEY` in .env
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Set up production database (PostgreSQL recommended)
- [ ] Configure email settings for notifications
- [ ] Enable HTTPS security settings
- [ ] Run `python manage.py check --deploy`
- [ ] Test all features in staging environment

### Environment Variables (.env)

Create a `.env` file with:

```env
DEBUG=False
SECRET_KEY=your-unique-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (Production)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=multibliz_pos
DB_USER=your_db_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Security (for HTTPS)
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
```

### Database Migration to PostgreSQL (Production)

#### Quick Setup with Automated Script ⚡

We provide an automated script that handles PostgreSQL setup and SQLite migration:

```bash
python scripts/setup_postgresql.py
```

The script will:
- ✅ Check PostgreSQL installation
- ✅ Test database connection
- ✅ Guide you through database creation
- ✅ Migrate tables automatically
- ✅ Optionally import data from SQLite
- ✅ Verify migration success

#### Manual Setup Instructions

1. **Install PostgreSQL**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   
   # Windows
   # Download from https://www.postgresql.org/download/windows/
   # Recommended: PostgreSQL 15 or 16
   ```

2. **Create Database**
   
   Open PostgreSQL command line (`psql`):
   
   ```sql
   -- Connect to PostgreSQL
   psql -U postgres
   
   -- Create database
   CREATE DATABASE multibliz_pos;
   
   -- Create user (or use existing postgres user)
   CREATE USER multibliz_user WITH PASSWORD 'your_secure_password';
   
   -- Configure user settings
   ALTER ROLE multibliz_user SET client_encoding TO 'utf8';
   ALTER ROLE multibliz_user SET default_transaction_isolation TO 'read committed';
   ALTER ROLE multibliz_user SET timezone TO 'Asia/Manila';
   
   -- Grant privileges
   GRANT ALL PRIVILEGES ON DATABASE multibliz_pos TO multibliz_user;
   
   -- Exit psql
   \q
   ```

3. **Install PostgreSQL Adapter**
   
   The package is already included in requirements.txt:
   ```bash
   pip install psycopg2-binary
   ```

4. **Configure Environment Variables**
   
   Edit your `.env` file and uncomment/add these lines:
   ```env
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=multibliz_pos
   DB_USER=multibliz_user
   DB_PASSWORD=your_secure_password
   DB_HOST=localhost
   DB_PORT=5432
   ```

5. **Database Migration Options**

   **Option A: Fresh Installation (Empty Database)**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

   **Option B: Migrate from SQLite (Import Existing Data)**
   ```bash
   # 1. Export data from SQLite (while still using SQLite)
   python manage.py dumpdata --natural-foreign --natural-primary \
          --exclude=contenttypes --exclude=auth.permission \
          --indent=2 > data_export.json
   
   # 2. Switch to PostgreSQL in .env (uncomment PostgreSQL settings)
   
   # 3. Create tables
   python manage.py migrate
   
   # 4. Import data
   python manage.py loaddata data_export.json
   
   # 5. Verify data
   python scripts/deployment_check.py
   ```

   **Option C: Use Automated Script (Recommended)**
   ```bash
   python scripts/setup_postgresql.py
   ```

6. **Test Connection**
   ```bash
   python manage.py dbshell  # Should connect to PostgreSQL
   ```

#### Troubleshooting PostgreSQL

**Connection Refused**
- Ensure PostgreSQL service is running:
  ```bash
  # Linux
  sudo systemctl status postgresql
  sudo systemctl start postgresql
  
  # Windows
  # Check Services app for "postgresql-x64-15" or similar
  ```

**Authentication Failed**
- Check `pg_hba.conf` allows local connections
- Verify username and password in `.env`
- Try connecting with: `psql -U multibliz_user -d multibliz_pos`

**Database Does Not Exist**
- Create database first (see step 2)
- Check database name matches `.env` setting

**ImportError: No module named psycopg2**
- Install: `pip install psycopg2-binary`
- Update: `pip freeze > requirements.txt`

#### Switching Back to SQLite

If you need to switch back to SQLite:

1. Comment out PostgreSQL settings in `.env`:
   ```env
   # DB_ENGINE=django.db.backends.postgresql
   # DB_NAME=multibliz_pos
   # ...
   ```

2. Restart your application - it will automatically use SQLite

### Web Server Setup (Production)

#### Option 1: Using Gunicorn (Linux)

1. **Install Gunicorn**
   ```bash
   pip install gunicorn
   ```

2. **Create Gunicorn Service**
   ```bash
   sudo nano /etc/systemd/system/multibliz.service
   ```

   ```ini
   [Unit]
   Description=Multibliz POS Gunicorn daemon
   After=network.target

   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/path/to/Multibliz POS System
   ExecStart=/path/to/.venv/bin/gunicorn \
             --workers 3 \
             --bind 0.0.0.0:8000 \
             multibliz_pos.wsgi:application

   [Install]
   WantedBy=multi-user.target
   ```

3. **Start Service**
   ```bash
   sudo systemctl start multibliz
   sudo systemctl enable multibliz
   ```

#### Option 2: Using Nginx + Gunicorn

1. **Configure Nginx**
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;

       location = /favicon.ico { access_log off; log_not_found off; }
       
       location /static/ {
           alias /path/to/Multibliz POS System/staticfiles/;
       }

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

2. **Enable SSL with Let's Encrypt**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d yourdomain.com
   ```

#### Option 3: Windows IIS

1. Install `wfastcgi` module
2. Configure IIS site
3. Set up URL Rewrite rules
4. Configure static files handling

### Security Hardening

1. **Change DEBUG to False**
   ```env
   DEBUG=False
   ```

2. **Set Strong SECRET_KEY**
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

3. **Configure ALLOWED_HOSTS**
   ```env
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   ```

4. **Enable HTTPS Security**
   ```env
   CSRF_COOKIE_SECURE=True
   SESSION_COOKIE_SECURE=True
   SECURE_SSL_REDIRECT=True
   ```

5. **Run Security Check**
   ```bash
   python manage.py check --deploy
   ```

### Backup Strategy

1. **Database Backups**
   ```bash
   # Automated daily backup script
   #!/bin/bash
   DATE=$(date +%Y%m%d_%H%M%S)
   pg_dump multibliz_pos > backup_$DATE.sql
   ```

2. **Media Files Backup**
   ```bash
   tar -czf media_backup_$DATE.tar.gz media/
   ```

3. **Schedule with Cron**
   ```bash
   0 2 * * * /path/to/backup_script.sh
   ```

### Monitoring

1. **Error Logging**
   - Configure Django logging in settings.py
   - Use services like Sentry for error tracking

2. **Performance Monitoring**
   - Enable Django Debug Toolbar in development
   - Use New Relic or AppDynamics for production

3. **Uptime Monitoring**
   - Use UptimeRobot or Pingdom

## 🔧 Maintenance

### Regular Tasks

- **Update Dependencies**
  ```bash
  pip install --upgrade -r requirements.txt
  ```

- **Database Optimization**
  ```bash
  python manage.py dbshell
  VACUUM ANALYZE;
  ```

- **Clear Old Forecasts**
  - Forecasts older than today are auto-deleted
  - Regenerate monthly for accuracy

### Troubleshooting

- **Static files not loading**: Run `python manage.py collectstatic`
- **Database errors**: Check connection settings in .env
- **Email not sending**: Verify SMTP credentials
- **Forecasts not generating**: Check historical sales data exists

## 📞 Support

For issues or questions:
- Check logs in `logs/` directory
- Review Django error pages (if DEBUG=True)
- Contact system administrator

## 🎯 System Requirements

**Minimum:**
- Python 3.10+
- 2GB RAM
- 10GB Storage
- SQLite (development)

**Recommended (Production):**
- Python 3.11+
- 4GB+ RAM
- 50GB+ Storage
- PostgreSQL 13+
- Nginx + Gunicorn
- SSL Certificate

---

**Version:** 1.0.0  
**Last Updated:** November 2025
