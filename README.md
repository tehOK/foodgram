[![Main Foodgram Workflow](https://github.com/tehOK/foodgram/actions/workflows/main.yaml/badge.svg)](https://github.com/tehOK/foodgram/actions/workflows/main.yaml)
# Foodgram

**Foodgram** — это веб-приложение для публикации, поиска и управления рецептами. Пользователи могут делиться рецептами, добавлять их в избранное, формировать список покупок, подписываться на других авторов и получать короткие ссылки на рецепты.

## Описание проекта

Foodgram — социальная платформа для любителей готовить. Здесь можно:
- Публиковать свои рецепты с фото, ингредиентами и тегами.
- Искать рецепты по названию, тегам, автору, избранному и списку покупок.
- Добавлять рецепты в избранное и формировать список покупок.
- Подписываться на других пользователей и следить за их новыми рецептами.
- Получать короткие ссылки на рецепты для быстрого доступа и делиться ими.
- Администрировать ингредиенты, теги и рецепты через удобную панель администратора.

## Стек технологий

- **Python 3.9**
- **Django** и **Django REST Framework**
- **PostgreSQL** (или SQLite для тестов)
- **Docker** и **docker-compose**
- **nginx** (gateway)
- **React** (frontend)
- **Djoser** (авторизация и работа с пользователями)
- **Gunicorn** (wsgi сервер)
- **django-filter** (фильтрация API)
- **JWT** (токены авторизации)

## Как развернуть проект

1. **Клонируйте репозиторий:**
   ```sh
   git clone https://github.com/tehOK/foodgram.git
   cd foodgram
   ```
2. **Создайте и активируйте виртуальное окружение:**
   ```sh
   python -m venv venv
   source venv/bin/activate
   ```
3. **Установите зависимости:**
   ```sh
   pip install -r requirements.txt
   ```
4. **Настройте базу данных:**
   - Для использования PostgreSQL создайте базу данных и пользователя:
     ```sh
     sudo -u postgres psql
     CREATE DATABASE foodgram;
     CREATE USER foodgram_user WITH ENCRYPTED PASSWORD 'foodgram_password';
     GRANT ALL PRIVILEGES ON DATABASE foodgram TO foodgram_user;
     \q
     ```
   - Для использования SQLite просто убедитесь, что файл `db.sqlite3` существует в корне проекта.
5. **Настройте переменные окружения:**
   - Создайте файл `.env` в корне проекта и добавьте в него следующие строки:
     ```env
     SECRET_KEY=your_secret_key
     DEBUG=True
     ALLOWED_HOSTS=127.0.0.1 localhost yourdomain.com
     USE_SQLITE=False
     
     POSTGRES_DB=foodgram
     POSTGRES_USER=foodgram_user
     POSTGRES_PASSWORD=foodgram_password
     DB_HOST=db
     DB_PORT=5432
     ```
6. **Запустите проект:**
   ```sh
   docker-compose up -d
   ```
7. **Примените миграции и создайте суперпользователя:**
   ```sh
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser
   ```
8. **Наполните базу данных ингредиентами и тегами (по желанию):**
   ```sh
   docker-compose exec web python manage.py load_ingredients
   docker-compose exec web python manage.py load_tags
   ```
9. **Откройте приложение в браузере:**
   - Перейдите по адресу `http://localhost/` для доступа к приложению.
   - Перейдите по адресу `http://localhost/admin/` для доступа к панели администратора.

## Как использовать API

API доступен по адресу `/api/`. Для доступа к нему используйте токены авторизации JWT. Пример запроса:
```http
GET /api/recipes/ HTTP/1.1
Host: localhost
Authorization: Bearer your_jwt_token
```

## Примечания

- Для работы с Docker необходимо установить Docker и docker-compose.
- Для работы с базой данных PostgreSQL необходимо установить PostgreSQL.
- Для работы с виртуальным окружением необходимо установить Python 3.9 и pip.
- Рекомендуется использовать файл `.env` для хранения секретных ключей и паролей.
- При развертывании на продакшн-сервере рекомендуется установить `DEBUG=False` и настроить `ALLOWED_HOSTS`.

## Автор *Михаил Кириченко*.