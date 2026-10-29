# Full-Stack E-Commerce Platform (ReactJS + FastAPI + Django + PostgreSQL/MySQL)

## 1. Project Abstract
An end-to-end E-Commerce Web Application enabling customers to browse products, filter by category, manage shopping carts, and securely place orders with online payment (Stripe/Razorpay) or Cash on Delivery (COD), alongside a comprehensive Admin Module for managing inventory, categories, order fulfillment, user access, and real-time sales analytics.

### System Architecture
```
ReactJS (Frontend UI - Customer & Admin Portals)
       │
       ▼
FastAPI (High-Performance Business APIs, Cart, Orders, Analytics)
       │
       ▼
Django (Authentication, JWT Issuance, ORM & Native Admin Management)
       │
       ▼
Database (PostgreSQL / MySQL Relational Storage)
```

---

## 2. Directory Structure
```text
ecommerce_fullstack/
├── docker-compose.yml              # Multi-container orchestration (Postgres, Django, FastAPI, React)
├── database/
│   └── schema.sql                  # Full DDL & seed script for User, Category, Product, Cart, Order, Order_Items
├── backend_django/                 # Django Authentication & Admin Service (Port 8001)
│   ├── manage.py
│   ├── requirements.txt
│   ├── ecommerce_auth/
│   │   ├── settings.py
│   │   └── urls.py
│   └── core/
│       ├── models.py               # Shared database models
│       ├── serializers.py          # DRF serializers & password hashing
│       ├── views.py                # Signup, Login, Logout, JWT verification, User management
│       └── admin.py                # Django Admin panel customizations
├── backend_fastapi/                # FastAPI Business Logic Service (Port 8000)
│   ├── requirements.txt
│   ├── database.py                 # SQLAlchemy engine & session setup (PostgreSQL / MySQL)
│   ├── models.py                   # SQLAlchemy ORM models matching exact schema
│   ├── schemas.py                  # Pydantic v2 validation schemas
│   ├── security.py                 # JWT verification, bcrypt password hashing, RBAC dependencies
│   └── main.py                     # Customer & Admin REST APIs (Products, Cart, Orders, Payments, Reports)
└── frontend_react/                 # ReactJS Single-Page Application (Port 3000)
    ├── package.json
    └── src/
        ├── api.js                  # Axios/Fetch API client with JWT interceptor
        └── App.jsx                 # Full React UI (Customer Storefront + Admin Dashboard)
```

---

## 3. Quick Start Guide

### Option A: Run with Docker Compose
```bash
docker-compose up --build
```
- **React Frontend**: `http://localhost:3000`
- **FastAPI Business APIs & Swagger Docs**: `http://localhost:8000/docs`
- **Django Auth & Admin Panel**: `http://localhost:8001/admin`

### Option B: Manual Local Setup

#### 1. Database Setup (PostgreSQL or MySQL)
Run `database/schema.sql` in your PostgreSQL or MySQL instance:
```bash
psql -U postgres -d ecommerce_db -f database/schema.sql
```

#### 2. Start Django Auth & Admin Service
```bash
cd backend_django
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 8001
```

#### 3. Start FastAPI Business API Service
```bash
cd backend_fastapi
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

#### 4. Start React Frontend
```bash
cd frontend_react
npm install
npm run dev
```
