# Access Rights in DRF

Django REST Framework project demonstrating user authentication, permissions, and access rights management.

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
git clone https://github.com/yourusername/31_Access_rights_in_DRF.git
cd 31_Access_rights_in_DRF
````

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
CREATE DATABASE access_rights OWNER stayer;
GRANT ALL PRIVILEGES ON DATABASE access_rights TO stayer;
```

### 3. Настраиваем схему `public`

```sql
ALTER DATABASE access_rights OWNER TO stayer;
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
        'NAME': 'access_rights',
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

## ✅ Тестирование (Pytest)

Если используете **pytest**, запустите тесты:

```bash
pytest
```

Для удобства добавьте файл `pytest.ini` в корень проекта:

```ini
[pytest]
DJANGO_SETTINGS_MODULE = project_name.settings
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

---