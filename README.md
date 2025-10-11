
# 🎓 Django REST API — Courses & Lessons

Проект представляет собой **REST API для образовательной платформы**, где реализованы модели **курсов** и **уроков**, а также кастомная модель **пользователя** с авторизацией по email.

---

## 📁 Структура проекта

```

andreystyuhin-30_1_viewsets_and_generics/
├── Dockerfile
├── docker-compose.yml
├── manage.py
├── .env.example
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── materials/        # Приложение для курсов и уроков
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
└── users/            # Кастомная модель пользователя
    ├── models.py
    └── admin.py

```

---

## 🚀 Основной функционал

- **Курсы (`Course`)**
  - CRUD-операции через `ModelViewSet`
  - Автоматическая связь с уроками
  - Вывод количества уроков и списка уроков в сериализаторе

- **Уроки (`Lesson`)**
  - CRUD через `ListCreateAPIView` и `RetrieveUpdateDestroyAPIView`
  - Поля: `title`, `description`, `video_url`, `preview`, `course`

- **Пользователи (`User`)**
  - Кастомная модель без `username`
  - Авторизация по `email`
  - Поля: `email`, `phone`, `city`, `avatar`
  - Вывод истории платежей в профиле

- **Платежи (`Payment`)**
  - Модель для хранения платежей
  - Фильтрация и сортировка в API

---

## ⚙️ Установка и запуск проекта

### Вариант 1: Локальная установка (без Docker)

#### 1. Клонировать репозиторий
```bash
git clone https://github.com/your-username/andreystyuhin-30_1_viewsets_and_generics.git
cd andreystyuhin-30_1_viewsets_and_generics
```

#### 2. Настроить PostgreSQL
- Установите PostgreSQL на вашей машине.
- Создайте базу данных:
  ```bash
  sudo su - postgres
  psql
  CREATE DATABASE lms_db;
  CREATE USER postgres WITH PASSWORD 'your_password_here';
  GRANT ALL PRIVILEGES ON DATABASE lms_db TO postgres;
  \q
  ```
- Скопируйте `.env.example` в `.env` и отредактируйте переменные (SECRET_KEY, DB_PASSWORD и т.д.).

#### 3. Создать и активировать виртуальное окружение
```bash
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
.venv\Scripts\activate      # Windows
```

#### 4. Установить зависимости
```bash
pip install -r requirements.txt
```

#### 5. Применить миграции
```bash
python manage.py makemigrations
python manage.py migrate
```

#### 6. Загрузить фикстуры (для тестовых данных платежей)
```bash
python manage.py loaddata users/fixtures/payments.json
```

#### 7. Создать суперпользователя
```bash
python manage.py createsuperuser
```

#### 8. Запустить сервер
```bash
python manage.py runserver
```

Сервер будет доступен по адресу: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

### Вариант 2: Запуск с Docker и PostgreSQL

#### 1. Клонировать репозиторий (если не сделано)
```bash
git clone https://github.com/your-username/andreystyuhin-30_1_viewsets_and_generics.git
cd andreystyuhin-30_1_viewsets_and_generics
```

#### 2. Настроить .env
Скопируйте `.env.example` в `.env` и отредактируйте переменные (SECRET_KEY, DB_PASSWORD и т.д.).

#### 3. Собрать и запустить контейнеры
```bash
docker-compose up --build
```

#### 4. Применить миграции (в отдельном терминале)
```bash
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

#### 5. Загрузить фикстуры
```bash
docker-compose exec web python manage.py loaddata users/fixtures/payments.json
```

#### 6. Создать суперпользователя
```bash
docker-compose exec web python manage.py createsuperuser
```

Сервер будет доступен по адресу: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 🧠 Примеры API-запросов

| Метод       | Endpoint             | Описание               |
| ----------- | -------------------- | ---------------------- |
| `GET`       | `/api/courses/`      | Получить список курсов |
| `POST`      | `/api/courses/`      | Создать новый курс     |
| `GET`       | `/api/courses/{id}/` | Получить курс по ID    |
| `PUT/PATCH` | `/api/courses/{id}/` | Изменить курс          |
| `DELETE`    | `/api/courses/{id}/` | Удалить курс           |
| `GET`       | `/api/lessons/`      | Получить список уроков |
| `POST`      | `/api/lessons/`      | Создать новый урок     |
| `GET`       | `/api/lessons/{id}/` | Получить урок          |
| `PUT/PATCH` | `/api/lessons/{id}/` | Изменить урок          |
| `DELETE`    | `/api/lessons/{id}/` | Удалить урок           |
| `GET`       | `/api/users/payments/` | Получить список платежей (с фильтрами) |

---

## 🧩 Используемые технологии

* [Python 3.13](https://www.python.org/)
* [Django 5.2](https://www.djangoproject.com/)
* [Django REST Framework](https://www.django-rest-framework.org/)
* [PostgreSQL](https://www.postgresql.org/) (как основная БД)
* [Docker](https://www.docker.com/)

---

## 🔒 Roadmap развития

| Этап                       | Задачи                                     | Статус   |
| -------------------------- | ------------------------------------------ | -------- |
| ✅ 1. Базовые модели и CRUD | Курсы, уроки, сериализаторы, ViewSets      | Готово   |
| 🔄 2. Кастомный User       | Email вместо username                      | Готово   |
| ✅ 3. Платежи               | Модель платежей, фикстуры, фильтры         | Готово   |
| ✅ 4. Интеграция с PostgreSQL | Настройка БД, Docker Compose               | Готово   |
| ⏳ 5. JWT аутентификация    | Подключить `djangorestframework-simplejwt` | В планах |
| ⏳ 6. Тестирование          | Настроить `pytest` и `coverage`            | В планах |
| ⏳ 7. Документация API      | Подключить Swagger / drf-spectacular       | В планах |

---

## 🧪 Тестирование

Настройка `pytest`:

```bash
pip install pytest pytest-django
```

Запуск тестов:

```bash
pytest -v
```

---

## 📂 Медиа и статика

* Медиафайлы: `/media/`
* Превью курсов и уроков сохраняются в:

  * `media/courses/`
  * `media/lessons/`
  * `media/avatars/`

В Docker: media volume настроен в docker-compose.yml.

---

## 👨‍💻 Автор

**Андрей Стюхин**
📧 Email: [andreyst@olovyannaya.ru](mailto:andreyst@olovyannaya.ru)

---

## 📝 Лицензия

Проект распространяется под лицензией **MIT**.
Вы можете использовать и модифицировать код с указанием автора.

---

## ⭐ Поддержка проекта

Если проект был полезен — поставь звезду ⭐ на GitHub!

```