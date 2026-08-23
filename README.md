# Stock Master — Inventory Management System

A production-quality, full-stack web application for managing inventory, tracking stock movements, and generating reports. Built with **Python (Flask)**, **MySQL/SQLite**, and **Vanilla HTML/CSS/JS (Tailwind CSS)**.

---

## Feature Overview

| Feature | Details |
|---|---|
| Authentication | Register and login with bcrypt password hashing, JWT tokens, roles (Admin/Staff) |
| Dashboard | Live KPI cards (Total Value, Low Stock, SKU Count, Out-of-Stock), Chart.js charts |
| Product Management | Full CRUD with SKU, name, category, supplier, unit, price, quantity, reorder threshold |
| Category Management | Full CRUD, product count per category |
| Supplier Management | Full CRUD with contact info, email, phone, address |
| Stock In / Out | Record every movement with type, quantity, reason, timestamp, and logged-by user |
| Low Stock Alerts | Auto-flag products at or below reorder level |
| Search and Filter | Global search bar + per-view filters (category, stock status) |
| Analytics | Most-active product rankings, stock movement trends, category distribution |
| PDF Export | Server-side PDF generation (ReportLab) for products, low stock, and stock history |
| Activity Log | Full audit trail of all system events |

---

## Tech Stack

### Backend
- Python 3.10+ with Flask 3.x
- SQLAlchemy 2.x ORM with MySQL (production) / SQLite (development fallback)
- Flask-Bcrypt for password hashing
- PyJWT for stateless JWT authentication
- ReportLab for server-side PDF generation
- Modular Flask Blueprint architecture

### Frontend
- Vanilla HTML5 / JavaScript (ES6+) — no frameworks
- Tailwind CSS via CDN (Material Design 3 color tokens)
- Chart.js for interactive bar and doughnut charts
- Google Material Symbols icon font
- Google Fonts — Inter typeface
- SPA routing via hash navigation

### Database
- MySQL 8+ (production) via PyMySQL driver
- SQLite automatic fallback when MySQL is unavailable

---

## Project Structure

```
inventory management/
+-- backend/
¦   +-- app.py               # Flask application factory
¦   +-- config.py            # Environment-based configuration
¦   +-- db.py                # DB init, connection test, automatic seed
¦   +-- models/              # SQLAlchemy ORM models
¦   ¦   +-- user.py
¦   ¦   +-- product.py
¦   ¦   +-- category.py
¦   ¦   +-- supplier.py
¦   ¦   +-- stock_movement.py
¦   ¦   +-- activity_log.py
¦   +-- routes/              # Flask Blueprints (one per resource)
¦   ¦   +-- auth.py
¦   ¦   +-- products.py
¦   ¦   +-- categories.py
¦   ¦   +-- suppliers.py
¦   ¦   +-- stock.py
¦   ¦   +-- reports.py
¦   ¦   +-- dashboard.py
¦   ¦   +-- activity_log.py
¦   +-- utils/
¦       +-- auth_middleware.py
+-- frontend/
¦   +-- index.html           # Complete SPA - all views, modals, JS logic
+-- database/
¦   +-- schema.sql           # MySQL InnoDB schema
¦   +-- seed.sql             # Sample data
+-- requirements.txt
+-- README.md
```

---

## Quick Start

### Prerequisites
- Python 3.10+
- MySQL 8+ (optional — SQLite fallback is automatic)

### 1 — Install

```bash
git clone <repo-url>
cd "inventory management"
python -m venv .venv
.venv\Scripts\Activate.ps1   # Windows PowerShell
pip install -r requirements.txt
```

### 2 — Configure Database (Optional)

To use MySQL, set the environment variable before starting:

```powershell
$env:DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/inventory_db"
```

Then create the database:
```bash
mysql -u root -p inventory_db < database/schema.sql
mysql -u root -p inventory_db < database/seed.sql
```

### 3 — Start the Server

```bash
.venv\Scripts\python.exe backend\app.py
```

Open **http://localhost:5000** in your browser.

### 4 — Default Credentials

| Role  | Username | Password   |
|-------|----------|------------|
| Admin | admin    | admin123   |
| Staff | staff    | staff123   |

---

## REST API Reference

All endpoints prefixed with `/api`. Protected endpoints require:
```
Authorization: Bearer <jwt_token>
```

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/register | Register a new user |
| POST | /api/auth/login | Login and receive JWT token |

### Products
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/products | List products (search, category_id, status params) |
| POST | /api/products | Create product (Admin only) |
| PUT | /api/products/:id | Update product (Admin only) |
| DELETE | /api/products/:id | Delete product (Admin only) |

### Stock Movements
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/stock/movement | Record IN or OUT movement |
| GET | /api/stock/history | List movements (type, limit params) |

### Dashboard and Reports
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/dashboard/stats | KPI cards, charts, low stock, recent activity |
| GET | /api/reports/analytics | Summary stats and most-active products |
| GET | /api/reports/export-pdf?type=products | Download PDF report |
| GET | /api/activity-log | Full audit log |

---

## Database Schema

```
users            — id, username, email, password_hash, role, created_at
categories       — id, name, description, created_at
suppliers        — id, name, contact_name, email, phone, address, created_at
products         — id, sku, name, category_id, supplier_id, unit, price, quantity,
                   reorder_level, created_at, updated_at
stock_movements  — id, product_id, type (IN|OUT), quantity, reason, user_id, timestamp
activity_log     — id, user_id, action, entity_type, entity_id, details, timestamp
```

---

## Role-Based Access

| Feature | Admin | Staff |
|---------|-------|-------|
| View all pages | Yes | Yes |
| Add/Edit Products | Yes | Yes |
| Delete Products | Yes | No |
| Add/Edit/Delete Categories | Yes | No |
| Add/Edit/Delete Suppliers | Yes | No |
| Record Stock Movements | Yes | Yes |
| Export PDF Reports | Yes | Yes |
| View Activity Log | Yes | Yes |

---

## PDF Export

Three report types from the Analytics and PDF page or direct API:

- **Product Inventory** — Full catalog with prices, quantities, and status
- **Low Stock Alerts** — Products at or below their reorder threshold
- **Stock Movement History** — All IN/OUT movements with timestamps and reasons

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| DATABASE_URL | SQLite local | Full SQLAlchemy URI for MySQL |
| SECRET_KEY | dev-secret-key | JWT signing secret (change in production!) |
| FLASK_ENV | development | Set to production to disable debug mode |

---

## License

MIT — Free to use and modify for educational and commercial purposes.
