# PostgreSQL Setup Quick Reference

## 🚀 Quick Start (Recommended)

Run the automated setup script:
```powershell
python scripts/setup_postgresql.py
```

## 📋 Manual Setup Steps

### 1. Install PostgreSQL
Download from: https://www.postgresql.org/download/windows/
Recommended: PostgreSQL 15 or 16

### 2. Create Database

Open SQL Shell (psql):
```sql
CREATE DATABASE multibliz_pos;
CREATE USER postgres WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE multibliz_pos TO postgres;
```

### 3. Configure .env

Edit `.env` and uncomment these lines:
```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=multibliz_pos
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### 4. Migrate Data

**Fresh Install:**
```powershell
python manage.py migrate
python manage.py createsuperuser
```

**Import from SQLite:**
```powershell
python scripts/setup_postgresql.py
# Choose option 2: "Migrate from SQLite"
```

## ✅ Verify Setup

```powershell
# Test connection
python manage.py dbshell

# Check deployment status
python scripts/deployment_check.py
```

## 🔄 Switch Back to SQLite

Comment out PostgreSQL settings in `.env`:
```env
# DB_ENGINE=django.db.backends.postgresql
# DB_NAME=multibliz_pos
# ...
```

System will automatically use SQLite.

## 🆘 Troubleshooting

**Connection Refused:**
- Check PostgreSQL service is running (Services app)
- Verify port 5432 is not blocked

**Authentication Failed:**
- Check username/password in `.env`
- Try: `psql -U postgres -d multibliz_pos`

**Database Does Not Exist:**
- Create it first (see step 2)
- Check spelling matches `.env`

## 📚 Full Documentation

See `DEPLOYMENT.md` for detailed instructions and troubleshooting.
