# Latice sa Pričom - ERP System

A complete ERP application system for managing orders, inventory (warehouse), and business configuration.

## 📋 Project Overview

**Latice sa Pričom** is a Flask-based ERP system designed for small and medium-sized enterprises. It provides management for:
- 📦 **Orders** - Create, track, and manage order status
- 🏭 **Inventory (Warehouse)** - Track and manage stock levels
- 📧 **Email Notifications** - Automated notification sending
- ⚙️ **Configuration** - System settings

## 🚀 Technologies

- **Backend:** Flask 2.3.0+
- **Database:** SQLite (SQLAlchemy ORM)
- **Scheduler:** APScheduler 3.10.0+
- **Frontend:** HTML5, CSS, JavaScript
- **Python:** 3.8+

## 📁 Project Structure

```
ERP_latice.sa.pricom/
├── ERP_server.py              # Main Flask application
├── models.py                  # SQLAlchemy models (Order, LagerItem)
├── cli.py                     # Command-line interface
├── requirements.txt           # Python dependencies
├── setup & install scripts    # Installation scripts
│
├── blueprints/               # Flask modules
│   ├── orders.py            # Order management logic
│   ├── lager.py             # Inventory management logic
│   ├── email_notify.py      # Email notifications and scheduler
│   └── config.py            # System configuration
│
├── templates/               # HTML templates
│   ├── base.html           # Base template
│   ├── index.html          # Home page
│   ├── edit.html           # Edit items
│   ├── lager.html          # Inventory overview
│   ├── porudzbenice.html   # All orders
│   ├── realizovano.html    # Completed orders
│   ├── za_dostavu.html     # Orders for delivery
│   ├── podesavanja.html    # Settings
│   └── config.html         # Configuration
│
├── static/                 # Static assets
│   ├── script.js          # JavaScript logic
│   └── style.css          # CSS styles
│
├── scripts/               # Helper scripts
│   ├── add_missing_columns.py
│   ├── export_to_json.py
│   ├── migrate_json.py
│   ├── run_export.sh
│   └── start_ERP.sh
│
├── data/                 # Database (auto-created)
├── images/              # Order images (auto-created)
└── docs/               # Documentation
```

## 🛠️ Installation

### Prerequisites
- Python 3.8 or newer
- pip (Python package manager)

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd ERP_latice.sa.pricom
```

### Step 2: Install Dependencies
```bash
chmod +x install.sh
./install.sh
```

Or manually:
```bash
pip install -r requirements.txt
```

### Step 3: Run the Server
```bash
chmod +x scripts/start_ERP.sh
./scripts/start_ERP.sh
```

Or directly:
```bash
python3 ERP_server.py
```

The server will be available at `http://localhost:5000`

## 📚 Usage

### Home Page
Access the main page of the application where you can access all modules.

### Modules

#### 1. **Orders**
- View all orders
- Create new orders
- Track the status of each order
- Update customer information

#### 2. **Inventory (Warehouse)**
- Monitor stock levels
- Add new products
- Update quantities
- Track product locations

#### 3. **Email Notifications**
- Automated notification sending
- Scheduler for periodic tasks
- Email notification settings

#### 4. **Configuration**
- System parameter settings
- Save configuration in `.erp.conf`

## 🔧 Configuration

Configuration is stored in the `.erp.conf` file:
```
key1=value1
key2=value2
```

## 📊 Database

The application uses an SQLite database with the following models:

### Order
- `id` - Unique identifier
- `naziv` - Product name
- `cena` - Price
- `placeno` - Payment status
- `kupac` - Customer name
- `datum` - Order date
- `kolicina` - Quantity
- `boja` - Color
- `opis` - Description
- `slika` - Product image
- `status` - Order status (new, in_progress, completed, delivered)
- `lager_id` - Link to warehouse

### LagerItem (Warehouse Item)
- `id` - Unique identifier
- `naziv` - Product name
- `cena` - Price per unit
- `boja` - Color
- `kolicina` - Available quantity
- `lokacija` - Warehouse location
- `slika` - Product image

## 🔒 Security

- Local SQLite database
- Server-side input validation
- CSRF protection (enabled with additional configuration)

## 🐛 Troubleshooting

### Application won't start
```bash
# Clear cache and temporary files
rm -rf __pycache__/
rm -rf *.pyc

# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Database is corrupted
```bash
# Delete the database and recreate it
rm data/erp.db

# Restart the application
python3 ERP_server.py
```

### Email notifications not working
- Check `.erp.conf` configuration
- Verify SMTP settings
- Check log files

## 📝 CLI (Command Line Interface)

The application has a CLI interface for various operations:
```bash
python3 cli.py --help
```

## 📦 Backup & Restore

Create a database backup:
```bash
chmod +x backup.sh
./backup.sh
```

## 📄 Available Scripts

Available scripts for various operations:
- `install.sh` - Installation
- `uninstall.sh` - Uninstallation
- `start_ERP.sh` - Start server
- `backup.sh` - Create backup
- `export_to_json.py` - Export to JSON
- `migrate_json.py` - Migrate data

## 🤝 Contributing

Suggestions and fixes are welcome. Please:
1. Fork the repository
2. Create a new branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

## 📞 Support

For questions or issues, please:
- Open an issue on GitHub
- Contact the system administrator

## 📄 License

---

**© 2024-2026 Latice sa Pričom - ERP System**

All rights reserved. This project was developed for internal use.

**Version:** 1.0.0  
**Author:** ERP Development Team  
**Date:** February 2026

---

## ℹ️ Additional Information

- **Status:** Actively maintained
- **Support:** Available
- **Security Updates:** Regularly applied

Thank you for using Latice sa Pričom - ERP System!
