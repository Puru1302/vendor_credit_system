# 🏪 Smart Vendor Credit Management System

> A full-stack Django + MySQL web application for shops & restaurants to manage vendor purchases, GST, credit tracking, and predict payment risks using an AI-like scoring engine.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Django](https://img.shields.io/badge/Django-4.2-green?logo=django)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange?logo=mysql)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple?logo=bootstrap)

---

## 📸 Features

| Feature | Description |
|---|---|
| 🧾 Purchase Entry | Invoice-wise purchase tracking with line items |
| 🧮 Auto GST Calculation | Real-time GST calc (0%, 5%, 12%, 18%, 28%) |
| 💳 Credit/Debit Tracking | Outstanding balance per vendor |
| 🔔 Payment Reminders | Overdue alerts with days-late indicator |
| 📊 Daily Dashboard | Today's purchases, KPIs, and charts |
| 📈 Monthly Analytics | 12-month trend + category/payment mode breakdown |
| 📤 Export CSV | Download purchases & vendor data as CSV |
| 🗂️ Category-wise Items | SKU/item master with category and selling price |
| 🔍 Instant Vendor Search | Live search across all vendors |
| 🤖 AI Risk Vendor Score | Score (0–100) based on overdue days, outstanding ratio, payment history |
| 📅 Payment Prediction | Predict next payment date from historical patterns |

---

## 🗂️ Project Structure

```
vendor_credit_system/
├── manage.py
├── requirements.txt
├── setup_mysql.sql          # MySQL setup script
├── vendor_credit_system/    # Django project config
│   ├── settings.py
│   └── urls.py
└── vendor_app/              # Main application
    ├── models.py            # DB models (Vendor, Purchase, Payment, Item...)
    ├── views.py             # All view logic + API endpoints
    ├── forms.py             # Django forms
    ├── urls.py              # URL routing
    ├── admin.py             # Admin panel
    ├── management/
    │   └── commands/
    │       └── seed_demo.py # Demo data seeder
    └── templates/
        └── vendor_app/
            ├── base.html         # Sidebar layout
            ├── dashboard.html    # Main dashboard
            ├── vendor_list.html  # Vendor grid with risk scores
            ├── vendor_detail.html
            ├── vendor_form.html
            ├── purchase_list.html
            ├── purchase_detail.html
            ├── purchase_form.html # Live GST calculator
            ├── payment_form.html
            ├── analytics.html    # Monthly charts
            ├── item_list.html
            └── item_form.html
```

---

## ⚙️ Tech Stack

- **Frontend**: HTML5, CSS3, JavaScript (Vanilla), Bootstrap 5.3, Chart.js 4
- **Backend**: Python 3.10+, Django 4.2
- **Database**: MySQL 8.0 (via `mysqlclient`)
- **Fonts**: Plus Jakarta Sans + Space Mono (Google Fonts)

---

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/vendor-credit-system.git
cd vendor-credit-system
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
> ⚠️ If `mysqlclient` fails, install MySQL dev headers first:
> ```bash
> sudo apt install libmysqlclient-dev    # Ubuntu/Debian
> brew install mysql-client              # macOS
> ```

### 4. Set Up MySQL Database
```bash
mysql -u root -p < setup_mysql.sql
```

Or manually in MySQL shell:
```sql
CREATE DATABASE vendor_credit_db CHARACTER SET utf8mb4;
```

### 5. Configure Database in `settings.py`
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'vendor_credit_db',
        'USER': 'root',           # your MySQL username
        'PASSWORD': 'yourpass',   # your MySQL password
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 6. Run Migrations
```bash
python manage.py makemigrations vendor_app
python manage.py migrate
```

### 7. Create Superuser
```bash
python manage.py createsuperuser
```

### 8. (Optional) Load Demo Data
```bash
python manage.py seed_demo
```

### 9. Start the Server
```bash
python manage.py runserver
```
Open http://127.0.0.1:8000 🎉

---

## 📱 Pages & URLs

| URL | Description |
|---|---|
| `/` | Dashboard with KPIs, charts, risk alerts |
| `/vendors/` | Vendor grid with AI risk scores |
| `/vendors/add/` | Add new vendor |
| `/vendors/<id>/` | Vendor profile with purchase history |
| `/purchases/` | All purchases with filters |
| `/purchases/add/` | New purchase with live GST calculator |
| `/payments/add/` | Record payment |
| `/analytics/` | Monthly analytics with charts |
| `/items/` | Item/SKU master |
| `/export/purchases/` | Download CSV |
| `/admin/` | Django admin panel |

### API Endpoints

| Endpoint | Description |
|---|---|
| `GET /api/vendors/search/?q=` | Live vendor search |
| `GET /api/gst/?subtotal=&rate=` | GST calculator |
| `GET /api/risk/<vendor_id>/` | Risk score + prediction |

---

## 🤖 AI Risk Vendor Score — How It Works

The **Risk Score (0–100)** is calculated using 4 weighted factors:

```
Score = Overdue Factor (40pts)
      + Credit Utilization Factor (25pts)
      + Pending Invoice Count (20pts)
      + Payment Frequency (15pts)
```

| Score | Risk Level | Action |
|---|---|---|
| 0–30 | 🟢 LOW | Normal |
| 31–60 | 🟡 MEDIUM | Monitor closely |
| 61–100 | 🔴 HIGH | Immediate follow-up |

**Payment Prediction**: Calculates average gap between historical payments and projects the next payment date.

---

## 📤 Export Options

- **Purchases CSV**: Invoice number, vendor, dates, subtotal, GST, total, paid, balance, status
- **Vendors CSV**: Name, GSTIN, category, terms, total purchases, outstanding, risk score

---

## 🔐 Admin Panel

Access at `/admin/` with your superuser credentials.

Manage: Categories, Vendors, Purchases (with inline items), Payments, Items.

---

## 🛠️ Customization

- **GST Rates**: Modify `GST_CHOICES` in `models.py`
- **Risk Thresholds**: Update `RISK_SCORE` in `settings.py`
- **Add PDF Export**: Install `reportlab` and add a PDF view
- **WhatsApp Reminder**: Integrate Twilio/Gupshup API in `views.py`

---

## 🤝 Contributing

Pull requests welcome! For major changes, open an issue first.

---

## 📄 License

MIT License — free to use for commercial and personal projects.

---

## 👨‍💻 Author

Built with ❤️ using Django + MySQL
> Perfect for shops, restaurants, wholesalers, and small businesses.
