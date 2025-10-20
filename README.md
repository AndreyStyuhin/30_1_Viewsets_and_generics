
# Validations pagination and tests

Django REST Framework project demonstrating user authentication, permissions, access rights management, course subscriptions, and link validation.

---

## 🚀 Stack

- **Python 3.13**
- **Django 5.x**
- **Django REST Framework**
- **PostgreSQL**
- **JWT Authentication**

---

## ⚙️ Установка и запуск проекта

### 1. Клонируем репозиторий
```bash
git clone https://github.com/andreystyuhin/andreystyuhin-30_1_viewsets_and_generics.git
cd andreystyuhin-30_1_viewsets_and_generics
```

### 2. Создаём и активируем виртуальное окружение

```bash
python -m venv .venv
source .venv/bin/activate  # для Linux/Mac
# или
.venv\Scripts\activate     # для Windows
```

### 3. Устанавливаем зависимости

```bash
pip install -r requirements.txt
```

---

## 🗄️ Настройка базы данных PostgreSQL

### 1. Подключаемся к PostgreSQL

```bash
sudo -u postgres psql
```

### 2. Создаём пользователя и базу данных

```sql
CREATE USER stayer WITH PASSWORD 'your_password';
CREATE DATABASE lms_db OWNER stayer;
GRANT ALL PRIVILEGES ON DATABASE lms_db TO stayer;
```

### 3. Настраиваем схему `public`

```sql
ALTER DATABASE lms_db OWNER TO stayer;
ALTER SCHEMA public OWNER TO stayer;
GRANT ALL ON SCHEMA public TO stayer;
```

### 4. Проверяем, что пользователь имеет права

```sql
\dn+
\l
```

Вы должны увидеть, что:

* владелец схемы `public` — `stayer`
* владелец базы данных — `stayer`

---

## ⚙️ Настройки Django

Откройте `settings.py` и проверьте блок `DATABASES`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'lms_db',
        'USER': 'stayer',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

---

## 🧱 Миграции

Применяем миграции:

```bash
python manage.py makemigrations
python manage.py migrate
```

Если видите ошибку `нет доступа к схеме public` — убедитесь, что владелец базы данных и схемы совпадает с пользователем, указанным в `settings.py`.

---

## 👤 Создание суперпользователя

```bash
python manage.py createsuperuser
```

---

## ▶️ Запуск сервера

```bash
python manage.py runserver
```

Откройте в браузере:

```
http://127.0.0.1:8000/
```

---

## Новые функции

- **Валидация ссылок**: В уроках разрешены только YouTube-ссылки.
- **Подписки**: Эндпоинт /api/subscriptions/ для toggle подписки (POST с course_id).
- **Пагинация**: Для списков курсов и уроков (page_size=10).
- **Тесты**: Покрытие CRUD для уроков, подписок и других эндпоинтов (запустить pytest --cov).

---

## ✅ Тестирование (Pytest)

Если используете **pytest**, запустите тесты:

```bash
pytest --cov
```

Для удобства добавьте файл `pytest.ini` в корень проекта:

```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings
python_files = tests.py test_*.py *_tests.py
```

---

## 🧩 Полезные команды

```bash
# Проверка списка миграций
python manage.py showmigrations

# Просмотр подключённых приложений
python manage.py listapps

# Проверка прав пользователя PostgreSQL
sudo -u postgres psql -c "\du+"

# Проверка схем
sudo -u postgres psql -c "\dn+"
```

---

## 🪪 Автор

**Стюхин Андрей**

---

## 📝 Лицензия

Проект распространяется под лицензией MIT.

```