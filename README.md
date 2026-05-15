# 🏪 Smart Vendor Credit Management System

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Django](https://img.shields.io/badge/Django-4.2-green?logo=django)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange?logo=mysql)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple?logo=bootstrap)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

A powerful full-stack **Django + MySQL** web application designed for shops, restaurants, wholesalers, and small businesses to manage:

- Vendor purchases
- GST calculations
- Credit/debit balances
- Payment tracking
- Business analytics
- AI-style vendor risk prediction

---

# 🌟 Why This Project?

Many small businesses still manage vendor payments manually using notebooks or Excel sheets.

This system digitizes the entire vendor management workflow by providing:

✅ Automated GST calculations  
✅ Vendor balance tracking  
✅ Payment reminders  
✅ Analytics dashboard  
✅ AI-style vendor risk scoring  
✅ Purchase & payment reports  

---




---

# 🚀 Features

| Feature | Description |
|---|---|
| 🧾 Purchase Entry | Invoice-wise purchase management |
| 🧮 Auto GST Calculation | GST support (0%, 5%, 12%, 18%, 28%) |
| 💳 Credit/Debit Tracking | Outstanding balance tracking |
| 🔔 Payment Reminders | Overdue alerts & indicators |
| 📊 Dashboard Analytics | KPIs, charts & summaries |
| 📈 Monthly Reports | 12-month analytics tracking |
| 📤 CSV Export | Export vendor & purchase reports |
| 🔍 Live Vendor Search | Instant vendor search |
| 🗂️ Item Management | Category-wise inventory system |
| 🤖 AI Risk Score | Vendor payment risk prediction |
| 📅 Payment Prediction | Predict next expected payment date |

---

# 🛠️ Tech Stack

## Frontend
- HTML5
- CSS3
- JavaScript
- Bootstrap 5.3
- Chart.js

## Backend
- Python 3.10+
- Django 4.2

## Database
- MySQL 8.0
- mysqlclient

---

# 🏗️ System Architecture

```text
Frontend (HTML/CSS/JavaScript)
            ↓
      Django Backend
            ↓
       MySQL Database
```

---

# 📂 Project Structure

```text
smart-vendor-credit-management-system/
│
├── manage.py
├── requirements.txt
├── setup_mysql.sql
│
├── vendor_credit_system/
│   ├── settings.py
│   └── urls.py
│
├── vendor_app/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── admin.py
│   └── templates/
│
├── static/
└── screenshots/
```

---

# ⚙️ Installation & Setup

## 1️⃣ Clone Repository

```bash
git clone https://github.com/yourusername/smart-vendor-credit-management-system.git

cd smart-vendor-credit-management-system
```

---

## 2️⃣ Create Virtual Environment

### Windows
```bash
python -m venv venv

venv\Scripts\activate
```

### Linux/macOS
```bash
python3 -m venv venv

source venv/bin/activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4️⃣ Create MySQL Database

Open MySQL and run:

```sql
CREATE DATABASE vendor_credit_db CHARACTER SET utf8mb4;
```

---

## 5️⃣ Configure Database

Open:

```text
vendor_credit_system/settings.py
```

Update:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'vendor_credit_db',
        'USER': 'root',
        'PASSWORD': 'yourpassword',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

---

## 6️⃣ Run Migrations

```bash
python manage.py makemigrations

python manage.py migrate
```

---

## 7️⃣ Create Superuser

```bash
python manage.py createsuperuser
```

---

## 8️⃣ Run Development Server

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

---

# 📊 Dashboard Modules

| Module | Description |
|---|---|
| Vendor Management | Add/update vendor records |
| Purchase Management | Invoice-based purchases |
| Payment Tracking | Vendor payment records |
| GST Management | Automatic tax calculations |
| Analytics Dashboard | Business insights |
| CSV Reports | Exportable business reports |
| AI Risk Engine | Vendor risk prediction |

---

# 🔌 API Endpoints

| Endpoint | Description |
|---|---|
| `/api/vendors/search/?q=` | Live vendor search |
| `/api/gst/?subtotal=&rate=` | GST calculator |
| `/api/risk/<vendor_id>/` | Vendor risk score |

---

# 🤖 AI Risk Score Logic

The Vendor Risk Score (0–100) is calculated using:

```text
Risk Score =
Overdue Factor
+ Credit Utilization
+ Pending Invoice Count
+ Payment Frequency
```

## Risk Levels

| Score | Level |
|---|---|
| 0–30 | 🟢 Low |
| 31–60 | 🟡 Medium |
| 61–100 | 🔴 High |

---

# 📚 What I Learned

Through this project, I improved my skills in:

- Django Architecture
- MySQL Database Design
- CRUD Operations
- API Development
- Dashboard Analytics
- Business Logic Automation
- Git & GitHub Workflow
- Full-Stack Development

---

# 🚀 Future Enhancements

- PDF Invoice Generation
- WhatsApp Payment Reminders
- Email Notifications
- Barcode Billing System
- Role-Based Authentication
- Mobile Responsive Dashboard
- Advanced AI Payment Forecasting
- Multi-Branch Support

---

# 🌐 Deployment Platforms

This project can be deployed on:

- Render
- Railway
- PythonAnywhere
- AWS
- DigitalOcean

---

# 🤝 Contributing

Contributions, suggestions, and improvements are welcome.

Fork the repository and create a pull request.

---

# 📄 License

This project is licensed under the MIT License.

---

# 👨‍💻 Author

## B. Purushotham Reddy

Full-Stack Django Developer  
Python | Django | MySQL | Business Analytics

---

# ⭐ Support

If you like this project:

⭐ Star the repository  
🍴 Fork the project  
📢 Share it on LinkedIn

---
