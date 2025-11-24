# 🚀 Railway.app Deployment Guide - Multibliz POS System

## Prerequisites
- GitHub account
- Railway.app account (sign up at https://railway.app)
- Your code pushed to a GitHub repository

## Step 1: Prepare Your GitHub Repository

### 1.1 Initialize Git (if not already done)
```bash
git init
git add .
git commit -m "Initial commit - Ready for Railway deployment"
```

### 1.2 Create GitHub Repository
1. Go to https://github.com/new
2. Create a new repository (e.g., `multibliz-pos-system`)
3. Push your code:
```bash
git remote add origin https://github.com/YOUR_USERNAME/multibliz-pos-system.git
git branch -M main
git push -u origin main
```

## Step 2: Deploy to Railway

### 2.1 Create New Project
1. Go to https://railway.app
2. Click "Start a New Project"
3. Select "Deploy from GitHub repo"
4. Authorize Railway to access your GitHub
5. Select your `multibliz-pos-system` repository

### 2.2 Add PostgreSQL Database
1. In your Railway project, click "New"
2. Select "Database" → "Add PostgreSQL"
3. Railway will automatically provision a PostgreSQL database
4. The `DATABASE_URL` environment variable will be automatically created

### 2.3 Configure Environment Variables
Click on your web service → "Variables" tab and add:

```env
DEBUG=False
SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
ALLOWED_HOSTS=*

# Email Configuration (for password reset)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=multiblizinternationalcorp@gmail.com
EMAIL_HOST_PASSWORD=jagr lpgc ztjq uvuh
DEFAULT_FROM_EMAIL=multiblizinternationalcorp@gmail.com
```

**Note:** Railway automatically provides:
- `DATABASE_URL` (from PostgreSQL service)
- `RAILWAY_STATIC_URL` (your app's public URL)
- `PORT` (the port your app should listen on)

### 2.4 Generate a Strong SECRET_KEY
You can generate a strong secret key using Python:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Step 3: Deploy & Migrate Database

### 3.1 Initial Deployment
Railway will automatically:
1. Detect your Django app
2. Install dependencies from `requirements.txt`
3. Run `collectstatic` (configured in `railway.json`)
4. Start your app with Gunicorn

### 3.2 Run Database Migrations
After deployment, you need to run migrations:

1. Go to your Railway project
2. Click on your web service
3. Go to "Settings" → "Deploy"
4. Under "Custom Start Command", temporarily change to:
   ```
   python manage.py migrate && gunicorn multibliz_pos.wsgi --log-file -
   ```
5. Redeploy (this will run migrations)
6. After successful migration, you can remove the migrate command or leave it (it's safe)

### 3.3 Create Superuser
To create an admin account:

1. In Railway, click your service → "Settings" → "Deploy"
2. Add a one-time command:
   ```
   python manage.py createsuperuser
   ```
3. Or use the Railway CLI:
   ```bash
   railway run python manage.py createsuperuser
   ```

## Step 4: Access Your Deployed Application

### 4.1 Get Your Public URL
1. In Railway project, click "Settings" → "Networking"
2. Click "Generate Domain"
3. Your app will be available at: `https://YOUR-APP.railway.app`

### 4.2 Test Your Deployment
1. Visit your public URL
2. Login with your superuser credentials
3. Test all features:
   - POS Terminal
   - Product Management
   - Sales Records
   - Inventory
   - Forecasting
   - Reports

## Step 5: Import Your Existing Data (Optional)

If you want to migrate your SQLite data to Railway PostgreSQL:

### 5.1 Export Data from SQLite
On your local machine:
```bash
python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission > data_backup.json
```

### 5.2 Import to Railway PostgreSQL
1. Copy the JSON file to your project
2. Commit and push to GitHub
3. In Railway CLI or one-time command:
```bash
railway run python manage.py loaddata data_backup.json
```

## Step 6: Continuous Deployment

Railway automatically deploys when you push to GitHub:

```bash
git add .
git commit -m "Your changes"
git push origin main
```

Railway will automatically:
- Pull latest code
- Install dependencies
- Collect static files
- Restart your application

## Configuration Files Created

### ✅ Procfile
Tells Railway how to run your app:
```
web: gunicorn multibliz_pos.wsgi --log-file -
```

### ✅ railway.json
Configures build and deploy process:
```json
{
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt && python manage.py collectstatic --noinput"
  },
  "deploy": {
    "startCommand": "gunicorn multibliz_pos.wsgi --log-file -"
  }
}
```

### ✅ runtime.txt
Specifies Python version:
```
python-3.11.9
```

### ✅ nixpacks.toml
Additional Railway configuration for build process.

## Environment Variables Reference

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DEBUG` | Debug mode | Yes | False |
| `SECRET_KEY` | Django secret key | Yes | - |
| `DATABASE_URL` | PostgreSQL connection | Auto | - |
| `RAILWAY_STATIC_URL` | Public URL | Auto | - |
| `ALLOWED_HOSTS` | Allowed domains | Yes | * |
| `EMAIL_HOST` | SMTP host | No | - |
| `EMAIL_PORT` | SMTP port | No | 587 |
| `EMAIL_HOST_USER` | Email username | No | - |
| `EMAIL_HOST_PASSWORD` | Email password | No | - |

## Troubleshooting

### Issue: Static Files Not Loading
**Solution:** Railway automatically runs `collectstatic` during build. Check:
```bash
railway logs
```

### Issue: Database Connection Error
**Solution:** Verify PostgreSQL service is running and `DATABASE_URL` is set:
```bash
railway variables
```

### Issue: 500 Internal Server Error
**Solution:** Check logs for detailed error:
```bash
railway logs --tail
```

### Issue: CSRF Verification Failed
**Solution:** Ensure `CSRF_TRUSTED_ORIGINS` includes your Railway URL (automatically configured).

## Monitoring & Logs

### View Logs
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link to your project
railway link

# View logs
railway logs --tail
```

### Railway Dashboard
- Monitor CPU/Memory usage
- View deployment history
- Check build logs
- Manage environment variables

## Cost Estimation

Railway Free Tier includes:
- $5 of free usage per month
- 500 hours of usage
- Suitable for testing and small applications

For production:
- PostgreSQL: ~$5-10/month
- Web Service: ~$5-10/month (depending on usage)
- Total: ~$10-20/month for small to medium traffic

## Security Checklist

- ✅ `DEBUG=False` in production
- ✅ Strong `SECRET_KEY` generated
- ✅ HTTPS enforced (automatic on Railway)
- ✅ CSRF protection enabled
- ✅ XSS protection enabled
- ✅ PostgreSQL password secured
- ✅ Email credentials secured
- ✅ CORS configured (if needed)

## Post-Deployment Tasks

1. ✅ Test all POS features
2. ✅ Verify product search and adding to cart
3. ✅ Test payment processing
4. ✅ Check sales reports and forecasting
5. ✅ Verify inventory management
6. ✅ Test user authentication and permissions
7. ✅ Configure backup strategy
8. ✅ Set up monitoring alerts

## Backup Strategy

### Automated Backups
Railway PostgreSQL includes automatic daily backups.

### Manual Backup
```bash
# Export database
railway run python manage.py dumpdata > backup_$(date +%Y%m%d).json

# Download database dump
railway run pg_dump $DATABASE_URL > backup.sql
```

## Support & Resources

- **Railway Docs:** https://docs.railway.app
- **Django Deployment:** https://docs.djangoproject.com/en/5.2/howto/deployment/
- **Railway Discord:** https://discord.gg/railway
- **Railway Status:** https://status.railway.app

## Quick Command Reference

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login to Railway
railway login

# Link to project
railway link

# View logs
railway logs --tail

# Run migrations
railway run python manage.py migrate

# Create superuser
railway run python manage.py createsuperuser

# Open deployed app
railway open

# View environment variables
railway variables

# Add environment variable
railway variables set KEY=VALUE
```

## Success! 🎉

Your Multibliz POS System is now deployed on Railway.app!

**Next Steps:**
1. Share your Railway URL with your team
2. Create user accounts for staff
3. Import your product data
4. Start processing transactions
5. Monitor performance and usage

**Your Deployment URL:** `https://YOUR-APP.railway.app`

---

**Need Help?**
- Check Railway logs for errors
- Review Django debug pages (if DEBUG=True temporarily)
- Contact Railway support through their Discord
- Review this deployment guide

**Happy Selling! 💰**
