
# 🎓 Django REST API — Courses & Lessons

Проект представляет собой **REST API для образовательной платформы**, где реализованы модели **курсов** и **уроков**, а также кастомная модель **пользователя** с авторизацией по email.


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



## ⚙️ Установка и запуск проекта

### 1. Клонировать репозиторий
```
git clone https://github.com/your-username/andreystyuhin-30_1_viewsets_and_generics.git
cd andreystyuhin-30_1_viewsets_and_generics
```

### 2. Создать и активировать виртуальное окружение

```
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
.venv\Scripts\activate      # Windows
```

### 3. Установить зависимости

```
pip install -r requirements.txt
```

*(если файла `requirements.txt` нет — можно создать его командой `pip freeze > requirements.txt`)*

### 4. Применить миграции

```
python manage.py makemigrations
python manage.py migrate
```

### 5. Загрузить фикстуры (для тестовых данных платежей)

```
python manage.py loaddata users/fixtures/payments.json
```

### 6. Создать суперпользователя

```
python manage.py createsuperuser
```

### 7. Запустить сервер

```
python manage.py runserver
```

Сервер будет доступен по адресу:
👉 [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

```

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

```

## 🧩 Используемые технологии

* [Python 3.13](https://www.python.org/)
* [Django 5.2](https://www.djangoproject.com/)
* [Django REST Framework](https://www.django-rest-framework.org/)
* [Django Filter](https://django-filter.readthedocs.io/en/stable/)
* SQLite (по умолчанию)



## 🔒 Roadmap развития

| Этап                       | Задачи                                     | Статус   |
| -------------------------- | ------------------------------------------ | -------- |
| ✅ 1. Базовые модели и CRUD | Курсы, уроки, сериализаторы, ViewSets      | Готово   |
| 🔄 2. Кастомный User       | Email вместо username                      | Готово   |
| ✅ 3. Платежи               | Модель платежей, фикстуры, фильтры         | Готово   |
| ⏳ 4. JWT аутентификация    | Подключить `djangorestframework-simplejwt` | В планах |
| ⏳ 5. Тестирование          | Настроить `pytest` и `coverage`            | В планах |
| ⏳ 6. Документация API      | Подключить Swagger / drf-spectacular       | В планах |
| ⏳ 7. Docker                | Добавить Docker + Postgres                 | В планах |



## 🧪 Тестирование

Настройка `pytest`:

```
pip install pytest pytest-django
```

Запуск тестов:

```
pytest -v
```



## 📂 Медиа и статика

* Медиафайлы: `/media/`
* Превью курсов и уроков сохраняются в:

  * `media/courses/`
  * `media/lessons/`
  * `media/avatars/`



## 👨‍💻 Автор

**Андрей Стюхин**
📧 Email: [andreyst@olovyannaya.ru](mailto:andreyst@olovyannaya.ru)



## 📝 Лицензия

Проект распространяется под лицензией **MIT**.
Вы можете использовать и модифицировать код с указанием автора.



## ⭐ Поддержка проекта

Если проект был полезен — поставь звезду ⭐ на GitHub!

