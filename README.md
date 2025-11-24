# 🏪 Multibliz POS System

**Modern Point of Sale System with AI-Powered Forecasting**

A comprehensive Django-based POS system designed for retail businesses with integrated inventory management, sales tracking, and machine learning-powered demand forecasting.

## ✨ Features

### 🎯 Core Modules
- **Point of Sale (POS) Terminal** - Fast, intuitive sales processing
- **Product Management** - Complete product catalog with categorization
- **Inventory Management** - Real-time stock tracking and alerts
- **Sales Records** - Comprehensive transaction history
- **Returns Management** - Handle product returns and refunds
- **Supplier Management** - Track suppliers and purchase orders
- **User Management** - Role-based access control (Admin/Staff/Cashier)
- **Audit Trail** - Complete activity logging for accountability

### 🤖 Advanced Features
- **AI Forecasting** - ML-powered demand prediction using XGBoost & Prophet
- **Analytics Dashboard** - Real-time business insights and charts
- **Low Stock Alerts** - Automatic inventory monitoring
- **Revenue Tracking** - Detailed financial reporting
- **Dark Mode** - Modern UI with theme switching

### 🔒 Security
- Role-based permissions
- Secure authentication
- Audit logging
- CSRF protection
- Session management

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "Multibliz POS System"
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Collect static files**
   ```bash
   python manage.py collectstatic --noinput
   ```

8. **Run development server**
   ```bash
   python manage.py runserver
   ```

9. **Access the system**
   - Open browser: `http://127.0.0.1:8000`
   - Login with your superuser credentials

## 📊 Technology Stack

- **Backend:** Django 5.2.7, Python 3.14
- **Frontend:** Bootstrap 5, Chart.js, Font Awesome
- **Database:** SQLite (dev), PostgreSQL (production)
- **ML/AI:** XGBoost, Prophet, scikit-learn
- **APIs:** Django REST Framework

## 🎓 Usage

### For Cashiers
1. Access POS Terminal from sidebar
2. Search and add products
3. Process transactions
4. Print receipts

### For Managers
1. View Analytics Dashboard
2. Monitor inventory levels
3. Review sales reports
4. Manage suppliers

### For Administrators
1. Manage users and permissions
2. Configure system settings
3. Generate AI forecasts
4. Review audit trails

## 📈 AI Forecasting

The system uses two ML algorithms:
- **XGBoost** - Gradient boosting for pattern recognition
- **Prophet** - Facebook's time series forecasting

### Generating Forecasts
1. Navigate to Forecasting page
2. Click "Generate Forecasts" button
3. View predictions for next 30 days
4. Export data for analysis

### Validating Forecasts
```bash
python scripts/validate_forecasts.py
```

## 🛠️ Configuration

### Environment Variables
See `.env.example` for all available settings:
- `DEBUG` - Debug mode (False for production)
- `SECRET_KEY` - Django secret key
- `ALLOWED_HOSTS` - Permitted hosts
- `EMAIL_HOST` - SMTP server for emails
- Database credentials
- Security settings

### User Roles
- **Admin** - Full system access
- **Manager** - Sales, inventory, reports
- **Cashier** - POS terminal only

## 📁 Project Structure

```
Multibliz POS System/
├── accounts/           # User authentication & management
├── sales/             # POS, products, sales records, returns
├── inventory/         # Stock management, suppliers
├── forecasting/       # AI/ML forecasting engine
├── dashboard/         # Analytics & reporting
├── audit/            # Activity logging
├── Frontend/         # Static assets (CSS, JS)
├── templates/        # HTML templates
├── scripts/          # Utility scripts
├── multibliz_pos/    # Django project settings
└── manage.py         # Django management script
```

## 🔧 Maintenance

### Regular Tasks
- Generate forecasts monthly
- Review low stock alerts
- Check audit logs
- Backup database
- Update dependencies

### Useful Commands
```bash
# Run tests
python manage.py test

# Check for issues
python manage.py check --deploy

# Create backup
python manage.py dumpdata > backup.json

# Generate realistic sales data
python generate_realistic_sales.py

# Validate forecasts
python scripts/validate_forecasts.py

# System health check
python scripts/deployment_check.py
```

## 📝 Documentation

- [Deployment Guide](DEPLOYMENT.md) - Production setup instructions
- [API Documentation](docs/API.md) - REST API endpoints
- [User Manual](docs/USER_MANUAL.md) - End-user guide

## 🐛 Troubleshooting

### Common Issues

**Static files not loading:**
```bash
python manage.py collectstatic --noinput
```

**Database errors:**
- Check `.env` configuration
- Run `python manage.py migrate`

**Forecasts not generating:**
- Ensure sales data exists
- Check ML dependencies installed

**Email not sending:**
- Verify SMTP settings in `.env`
- Check firewall rules

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is proprietary software developed for Multibliz International Corporation.

## 👥 Authors

- Development Team - Multibliz International Corporation
- AI/ML Module - Data Science Team

## 🙏 Acknowledgments

- Django Framework
- Bootstrap Team
- Chart.js Contributors
- XGBoost & Prophet Teams

## 📞 Support

For technical support or inquiries:
- Email: multiblizinternationalcorp@gmail.com
- System: Multibliz POS v1.0

---

**Built with ❤️ for Multibliz International Corporation**
