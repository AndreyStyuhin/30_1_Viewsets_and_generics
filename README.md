
---

```markdown
# 🎓 Django REST API — Courses & Lessons

Проект представляет собой **REST API для образовательной платформы**, где реализованы модели **курсов** и **уроков**, а также кастомная модель **пользователя** с авторизацией по email.

---

## 📁 Структура проекта

```

andreystyuhin-30_1_viewsets_and_generics/
├── manage.py
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

````

---

## 🚀 Основной функционал

- **Курсы (`Course`)**
  - CRUD-операции через `ModelViewSet`
  - Автоматическая связь с уроками

- **Уроки (`Lesson`)**
  - CRUD через `ListCreateAPIView` и `RetrieveUpdateDestroyAPIView`
  - Поля: `title`, `description`, `video_url`, `preview`, `course`

- **Пользователи (`User`)**
  - Кастомная модель без `username`
  - Авторизация по `email`
  - Поля: `email`, `phone`, `city`, `avatar`

---

## ⚙️ Установка и запуск проекта

### 1. Клонировать репозиторий
```bash
git clone https://github.com/your-username/andreystyuhin-30_1_viewsets_and_generics.git
cd andreystyuhin-30_1_viewsets_and_generics
````

### 2. Создать и активировать виртуальное окружение

```bash
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
.venv\Scripts\activate      # Windows
```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

*(если файла `requirements.txt` нет — можно создать его командой `pip freeze > requirements.txt`)*

### 4. Применить миграции

```bash
python manage.py migrate
```

### 5. Создать суперпользователя

```bash
python manage.py createsuperuser
```

### 6. Запустить сервер

```bash
python manage.py runserver
```

Сервер будет доступен по адресу:
👉 [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

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

---

## 🧩 Используемые технологии

* [Python 3.13](https://www.python.org/)
* [Django 5.2](https://www.djangoproject.com/)
* [Django REST Framework](https://www.django-rest-framework.org/)
* SQLite (по умолчанию)

---

## 🔒 Roadmap развития

| Этап                       | Задачи                                     | Статус   |
| -------------------------- | ------------------------------------------ | -------- |
| ✅ 1. Базовые модели и CRUD | Курсы, уроки, сериализаторы, ViewSets      | Готово   |
| 🔄 2. Кастомный User       | Email вместо username                      | Готово   |
| ⏳ 3. JWT аутентификация    | Подключить `djangorestframework-simplejwt` | В планах |
| ⏳ 4. Тестирование          | Настроить `pytest` и `coverage`            | В планах |
| ⏳ 5. Документация API      | Подключить Swagger / drf-spectacular       | В планах |
| ⏳ 6. Docker                | Добавить Docker + Postgres                 | В планах |

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