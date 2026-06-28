# 🍺 Hop & Barley

> **Language / Мова:** [English](README.md) | Українська

Повноцінний інтернет-магазин інгредієнтів для домашнього пивоваріння — Django веб-інтерфейс + DRF REST API, на PostgreSQL & Docker.

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

> Безкоштовний хостинг — перше завантаження може зайняти ~40с.
> Логін для демо: **admin** / пароль у Render Dashboard.

---

## Зміст

- [Функціональність](#функціональність)
- [Технологічний стек](#технологічний-стек)
- [Структура проекту](#структура-проекту)
- [Швидкий старт — Docker](#швидкий-старт--docker)
- [Локальна розробка](#локальна-розробка)
- [REST API та JWT](#rest-api-та-jwt)
- [Адмін-панель](#адмін-панель)
- [Тести та лінтери](#тести-та-лінтери)
- [Деплой на Render](#деплой-на-render)
- [Чек-ліст](#чек-ліст)

---

## Функціональність

| Розділ | Що реалізовано |
|---|---|
| **Каталог** | Список товарів з пагінацією, пошук, фільтри за категорією та ціною, сортування за ціною / новизною / популярністю |
| **Сторінка товару** | Повна інформація, середній рейтинг у зірочках, відгуки — доступні лише після статусу "delivered" |
| **Кошик** | Сесійний кошик: додавання, видалення, зміна кількості, перевірка залишків, підрахунок суми |
| **Оформлення замовлення** | Форма доставки, створення замовлення, email-сповіщення покупцю та адміну |
| **Особистий кабінет** | Реєстрація, вхід/вихід (session auth), історія замовлень з фільтром, редагування профілю та паролю |
| **Адмін-панель** | Кастомний дашборд аналітики, рольові дозволи (суперюзер / Менеджер), пошук, фільтри, масові дії |
| **REST API** | JWT-захищені ендпоінти для товарів, замовлень, кошика, відгуків, користувачів; Swagger/OpenAPI |
| **Деплой** | Docker + docker-compose, Render Blueprint (`render.yaml`), WhiteNoise для статики |

---

## Технологічний стек

| Рівень | Технологія |
|---|---|
| Бекенд | Django 4.2, Python 3.11 |
| REST API | Django REST Framework 3.17, SimpleJWT |
| API документація | drf-spectacular (Swagger/OpenAPI) |
| База даних | PostgreSQL 15 |
| Автентифікація | Сесії (веб) + JWT (API) |
| Статичні файли | WhiteNoise |
| Контейнеризація | Docker, docker-compose |
| Деплой | Render (безкоштовний тир, Docker runtime) |
| Тестування | pytest-django, pytest-cov |
| Лінтери | flake8, mypy |

---

## Структура проекту

```
hop-and-barley/
├── api/                  # DRF ViewSets, серіалізатори, JWT ендпоінти
├── config/               # Django налаштування, URLs, WSGI
├── docker/               # entrypoint.sh (migrate → seed → запуск)
├── orders/               # Логіка замовлень і кошика, аналітика, адмін
├── pages/                # Статичні сторінки (Гайди, Спільнота)
├── payments/             # Модель оплати (мок)
├── products/             # Товари, категорії, каталог
├── reviews/              # Модель відгуків і форма відправки
├── static/               # CSS, JS, зображення товарів
├── templates/            # Django HTML шаблони
├── tests/                # API та інтеграційні тести
├── users/                # Реєстрація, профіль, зміна паролю
├── .github/workflows/    # GitHub Actions CI
├── docker-compose.yml
├── Dockerfile
├── render.yaml           # Render Blueprint для деплою
├── requirements.txt
└── manage.py
```

---

## Швидкий старт — Docker

Найшвидший спосіб запустити проект з демо-даними:

```bash
git clone https://github.com/marko-onechance/django_brew_shop.git
cd django_brew_shop
docker-compose up --build
```

При першому запуску entrypoint автоматично:
1. Виконує всі міграції бази даних
2. Наповнює каталог демо-товарами з зображеннями
3. Створює групу дозволів `Manager`
4. Створює демо-суперюзера (`admin` / `admin1234`)

Відкрий **http://localhost:8000** — магазин готовий.

---

## Локальна розробка

### Вимоги

- Python 3.11+
- PostgreSQL 15 (локально або через Docker)
- pip

### Налаштування

```bash
# 1. Клонування та створення віртуального середовища
git clone https://github.com/marko-onechance/django_brew_shop.git
cd django_brew_shop
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Встановлення залежностей
pip install -r requirements.txt

# 3. Налаштування середовища
cp .env.example .env
# Відредагуй .env — вкажи DATABASE_NAME / USER / PASSWORD / HOST

# 4. Міграції та демо-дані
python manage.py migrate
python manage.py seed_catalog
python manage.py create_roles
python manage.py create_demo_admin   # admin / admin1234

# 5. Запуск dev-сервера
python manage.py runserver
```

Відкрий **http://localhost:8000**

---

## REST API та JWT

Базовий URL: `/api/`
Інтерактивна документація: **http://localhost:8000/api/docs/**

### Процес автентифікації

```bash
# 1. Отримання токенів
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin1234"}'

# Відповідь:
# { "access": "eyJ...", "refresh": "eyJ..." }

# 2. Використання токена в запитах
curl http://localhost:8000/api/orders/ \
  -H "Authorization: Bearer eyJ..."

# 3. Оновлення access токена
curl -X POST http://localhost:8000/api/users/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "eyJ..."}'
```

### Основні ендпоінти

| Метод | URL | Авторизація | Опис |
|---|---|---|---|
| GET | `/api/products/` | — | Список товарів (пошук, фільтр, пагінація) |
| GET | `/api/products/{id}/` | — | Деталі товару |
| GET/POST | `/api/products/{id}/reviews/` | POST: JWT | Список або відправка відгуку |
| GET/POST | `/api/orders/` | JWT | Замовлення користувача |
| GET/PATCH/DELETE | `/api/orders/{id}/` | JWT | Одне замовлення |
| GET/POST/PATCH/DELETE | `/api/cart/` | — | Керування кошиком |
| POST | `/api/users/register/` | — | Реєстрація |
| POST | `/api/users/login/` | — | Отримання JWT токенів |
| POST | `/api/users/token/refresh/` | — | Оновлення access токена |
| GET | `/api/docs/` | — | Swagger UI |
| GET | `/api/schema/` | — | OpenAPI схема (JSON) |

---

## Адмін-панель

Доступна за адресою **http://localhost:8000/admin/**

- **Товари та категорії** — повний CRUD, завантаження зображень, автозаповнення slug, відстеження залишків
- **Замовлення** — інлайн позиції, масові дії (позначити як Shipped / Delivered), підрахунок виручки
- **Відгуки** — модерація, фільтр за рейтингом та товаром
- **Користувачі** — керування акаунтами та групами
- **Аналітика** — кастомний дашборд за адресою `/admin/orders/order/analytics/`:
  - Загальна виручка, кількість замовлень, виручка за 30 днів, кількість користувачів
  - Розбивка замовлень за статусами з виручкою по кожному
  - Топ-10 товарів за кількістю продажів і виручкою
  - Виручка за категоріями
  - Денна динаміка замовлень (останні 30 днів)

**Рольові дозволи:**

| Роль | Перегляд | Зміна | Додавання | Видалення |
|---|---|---|---|---|
| Суперюзер | ✅ все | ✅ все | ✅ все | ✅ все |
| Менеджер | ✅ замовлення, товари | ✅ замовлення, товари | ❌ | ❌ |
| Звичайний користувач | ❌ | ❌ | ❌ | ❌ |

---

## Тести та лінтери

```bash
# Запуск всіх тестів
python -m pytest

# Тести з покриттям
python -m pytest --cov=. --cov-report=term-missing

# Лінтер
flake8 .

# Перевірка типів
mypy . --ignore-missing-imports
```

**Поточний стан: 36 тестів, всі проходять.**

Що покривають тести:
- Product API (список, деталі, 404)
- Order API (перевірка авторизації, ізоляція між користувачами)
- Реєстрація користувача та JWT автентифікація
- Swagger / OpenAPI схема
- Моделі Product та Category
- Представлення каталогу товарів
- Реєстрація, вхід, вихід, сторінка акаунту
- Модель відгуків (створення, унікальність, середній рейтинг)

---

## Деплой на Render

Репозиторій містить `render.yaml` Blueprint — він автоматично розгортає безкоштовну PostgreSQL базу та веб-сервіс.

**Кроки:**

1. Запушити репозиторій на GitHub
2. Перейти на [render.com](https://render.com) → **New** → **Blueprint**
3. Підключити GitHub репозиторій
4. Render знаходить `render.yaml` і створює базу даних та веб-сервіс
5. Натиснути **Apply** — перший деплой займає ~3 хвилини

При кожному деплої Docker entrypoint виконує міграції та повторно наповнює каталог демо-даними — товари завжди доступні навіть після скидання ефемерного сховища.

**Змінні середовища, які Render встановлює автоматично:**

| Змінна | Джерело |
|---|---|
| `SECRET_KEY` | Генерується Render автоматично |
| `DATABASE_URL` | Підключений PostgreSQL сервіс |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `.onrender.com` |
| `SESSION_COOKIE_SECURE` | `True` |
| `CSRF_COOKIE_SECURE` | `True` |

---

## Чек-ліст

- [x] Проект запускається командою `docker-compose up`
- [x] База даних PostgreSQL
- [x] Каталог: фільтри, пошук, пагінація
- [x] Сторінка товару: інформація, відгуки, додавання в кошик
- [x] Кошик: керування товарами, підрахунок суми, перевірка залишків
- [x] Оформлення замовлення: створення, email-сповіщення, валідація форми
- [x] Особистий кабінет: реєстрація, вхід, історія замовлень, редагування профілю
- [x] REST API: JWT автентифікація, Swagger документація, обмеження доступу
- [x] Адмін-панель: аналітика, фільтри, кастомні дії, рольовий доступ
- [x] Swagger/OpenAPI документація доступна і працює
- [x] Анотації типів та докстрінги в коді
- [x] Лінтери (flake8/mypy) проходять без критичних помилок
- [x] 36 тестів — всі проходять
- [x] README повний та зрозумілий
- [x] Деплой налаштований для Render
