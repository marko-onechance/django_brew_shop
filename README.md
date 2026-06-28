# 🍺 Hop & Barley

> **Language / Мова:** English | [Українська](README_UK.md)

A full-stack e-commerce shop for home-brewing ingredients — Django web UI + DRF REST API, on PostgreSQL & Docker.

![CI](https://github.com/marko-onechance/django_brew_shop/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11-blue?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-4.2-092E20?logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-3.17-red?logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)
![tests](https://img.shields.io/badge/tests-36%20passed-brightgreen)
![lint](https://img.shields.io/badge/lint-flake8-yellow)
![types](https://img.shields.io/badge/types-mypy-blue)

### 🔗 [Live Demo](https://hop-and-barley.onrender.com)

> Free hosting — first load may take ~40s to wake.
> Demo login: **admin** / check Render dashboard for password.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Quick Start — Docker](#quick-start--docker)
- [Local Development](#local-development)
- [REST API & JWT](#rest-api--jwt)
- [Admin Panel](#admin-panel)
- [Tests & Linters](#tests--linters)
- [Deployment on Render](#deployment-on-render)
- [Checklist](#checklist)

---

## Features

| Area | What's included |
|---|---|
| **Catalog** | Product listing with pagination, search, category & price filters, sorting by price / newest / popularity |
| **Product page** | Full details, average star rating, review section — reviewable only after "delivered" status |
| **Cart** | Session-based cart: add, remove, update quantity, stock validation, live total |
| **Checkout** | Shipping form, order creation, email notification to user & admin |
| **Account** | Registration, login/logout (session auth), order history with status filter, profile & password edit |
| **Admin** | Custom analytics dashboard, role-based permissions (superuser / Manager), search, filters, bulk actions |
| **REST API** | JWT-protected endpoints for products, orders, cart, reviews, users; Swagger/OpenAPI docs |
| **Deployment** | Docker + docker-compose, Render Blueprint (`render.yaml`), WhiteNoise for static files |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 4.2, Python 3.11 |
| REST API | Django REST Framework 3.17, SimpleJWT |
| API Docs | drf-spectacular (Swagger/OpenAPI) |
| Database | PostgreSQL 15 |
| Auth | Session (web UI) + JWT (API) |
| Static files | WhiteNoise |
| Containerisation | Docker, docker-compose |
| Deployment | Render (free tier, Docker runtime) |
| Testing | pytest-django, pytest-cov |
| Linting | flake8, mypy |

---

## Project Structure

```
hop-and-barley/
├── api/                  # DRF ViewSets, serializers, JWT endpoints
├── config/               # Django settings, URLs, WSGI
├── docker/               # entrypoint.sh (migrate → seed → start)
├── orders/               # Order & cart logic, analytics view, admin
├── pages/                # Static content pages (Guides, Community)
├── payments/             # Payment model (mock)
├── products/             # Product & category models, catalog views
├── reviews/              # Review model & submission view
├── static/               # CSS, JS, product images
├── templates/            # Django HTML templates
├── tests/                # API & integration tests
├── users/                # Registration, profile, password change
├── .github/workflows/    # GitHub Actions CI
├── docker-compose.yml
├── Dockerfile
├── render.yaml           # Render deployment blueprint
├── requirements.txt
└── manage.py
```

---

## Quick Start — Docker

The fastest way to get a running instance with demo data:

```bash
git clone https://github.com/marko-onechance/django_brew_shop.git
cd django_brew_shop
docker-compose up --build
```

On first start the entrypoint automatically:
1. Runs all database migrations
2. Seeds the demo product catalog with images
3. Creates a `Manager` permission group
4. Creates a demo superuser (`admin` / `admin1234`)

Open **http://localhost:8000** — the shop is ready.

---

## Local Development

### Prerequisites

- Python 3.11+
- PostgreSQL 15 running locally (or use Docker just for DB)
- pip

### Setup

```bash
# 1. Clone & create virtual environment
git clone https://github.com/marko-onechance/django_brew_shop.git
cd django_brew_shop
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env — set DATABASE_NAME / USER / PASSWORD / HOST to match your local PG

# 4. Apply migrations and seed demo data
python manage.py migrate
python manage.py seed_catalog
python manage.py create_roles
python manage.py create_demo_admin   # creates admin / admin1234

# 5. Start the dev server
python manage.py runserver
```

Open **http://localhost:8000**

---

## REST API & JWT

Base URL: `/api/`  
Interactive docs: **http://localhost:8000/api/docs/**

### Authentication flow

```bash
# 1. Obtain tokens
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin1234"}'

# Response:
# { "access": "eyJ...", "refresh": "eyJ..." }

# 2. Use access token in subsequent requests
curl http://localhost:8000/api/orders/ \
  -H "Authorization: Bearer eyJ..."

# 3. Refresh an expired access token
curl -X POST http://localhost:8000/api/users/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "eyJ..."}'
```

### Key endpoints

| Method | URL | Auth | Description |
|---|---|---|---|
| GET | `/api/products/` | — | Product list (search, filter, paginate) |
| GET | `/api/products/{id}/` | — | Product detail |
| GET/POST | `/api/products/{id}/reviews/` | POST: JWT | List or submit a review |
| GET/POST | `/api/orders/` | JWT | User's orders |
| GET/PATCH/DELETE | `/api/orders/{id}/` | JWT | Single order |
| GET/POST/PATCH/DELETE | `/api/cart/` | — | Cart management |
| POST | `/api/users/register/` | — | Create account |
| POST | `/api/users/login/` | — | Obtain JWT tokens |
| POST | `/api/users/token/refresh/` | — | Refresh access token |
| GET | `/api/docs/` | — | Swagger UI |
| GET | `/api/schema/` | — | OpenAPI schema (JSON) |

---

## Admin Panel

Access at **http://localhost:8000/admin/**

- **Products & Categories** — full CRUD with image upload, slug auto-fill, stock tracking
- **Orders** — inline order items, bulk status actions (Mark as Shipped / Delivered), revenue action
- **Reviews** — moderation, filter by rating and product
- **Users** — manage accounts and group memberships
- **Analytics** — custom dashboard at `/admin/orders/order/analytics/` with:
  - Total revenue, total orders, revenue last 30 days, total users
  - Orders breakdown by status with per-status revenue
  - Top 10 products by units sold and revenue
  - Revenue by category
  - Daily orders chart (last 30 days)

**Role-based permissions:**

| Role | Can view | Can change | Can add | Can delete |
|---|---|---|---|---|
| Superuser | ✅ all | ✅ all | ✅ all | ✅ all |
| Manager | ✅ orders, products | ✅ orders, products | ❌ | ❌ |
| Regular user | ❌ | ❌ | ❌ | ❌ |

---

## Tests & Linters

```bash
# Run all tests
python -m pytest

# Run with coverage report
python -m pytest --cov=. --cov-report=term-missing

# Lint
flake8 .

# Type checking
mypy . --ignore-missing-imports
```

**Current test suite: 36 tests, all passing.**

Coverage areas:
- Product API (list, detail, 404)
- Order API (auth-guard, user isolation)
- User registration & JWT auth
- Swagger / schema endpoints
- Product & Category models
- Product catalog views
- User registration, login, logout, account page
- Review model (creation, uniqueness constraint, average rating)

---

## Deployment on Render

The repo includes a `render.yaml` Blueprint that provisions a free PostgreSQL database and a web service automatically.

**Steps:**

1. Push the repository to GitHub
2. Go to [render.com](https://render.com) → **New** → **Blueprint**
3. Connect your GitHub repository
4. Render detects `render.yaml` and creates both the database and the web service
5. Click **Apply** — first deploy takes ~3 minutes

On every deploy, the Docker entrypoint runs migrations and re-seeds demo data, so the demo catalog is always populated even after ephemeral storage resets.

**Environment variables set automatically by Render:**

| Variable | Source |
|---|---|
| `SECRET_KEY` | Auto-generated by Render |
| `DATABASE_URL` | Linked PostgreSQL service |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `.onrender.com` |
| `SESSION_COOKIE_SECURE` | `True` |
| `CSRF_COOKIE_SECURE` | `True` |

---

## Checklist

- [x] Project starts with `docker-compose up`
- [x] PostgreSQL database
- [x] Product catalog: filters, search, pagination
- [x] Product detail page: info, reviews, add-to-cart
- [x] Cart: manage items, calculate total, stock validation
- [x] Checkout: order creation, email notification, form validation
- [x] Account: registration, login, order history, profile editing
- [x] REST API: JWT auth, Swagger docs, permission scoping
- [x] Admin panel: analytics, filters, custom actions, role-based access
- [x] Swagger/OpenAPI docs accessible and functional
- [x] Type annotations and docstrings throughout
- [x] Linters (flake8/mypy) pass without critical errors
- [x] 36 tests — all passing
- [x] README is complete and clear
- [x] Deployment configured for Render
