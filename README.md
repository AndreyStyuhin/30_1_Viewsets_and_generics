
### Celery
Celery — инструмент для асинхронной обработки задач в приложениях на Python. Используем Celery для создания отложенных и периодических задач.

#### 🚀 Stack
- Python 3.13
- Django 5.x
- Django REST Framework
- PostgreSQL
- JWT Authentication
- Celery
- Redis (как брокер для Celery)
- Docker (для контейнеризации и оркестрации)

#### ⚙️ Установка и запуск проекта
##### 1. Клонируем репозиторий
```
git clone https://github.com/andreystyuhin/andreystyuhin-30_1_viewsets_and_generics.git
cd andreystyuhin-30_1_viewsets_and_generics
```

##### 2. Создаём и активируем виртуальное окружение
```
python -m venv .venv
source .venv/bin/activate  # для Linux/Mac
# или
.venv\Scripts\activate     # для Windows
```

##### 3. Устанавливаем зависимости
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 🗄️ Настройка базы данных PostgreSQL
##### 1. Подключаемся к PostgreSQL
```
sudo -u postgres psql
```

##### 2. Создаём пользователя и базу данных
```
CREATE USER stayer WITH PASSWORD 'your_password';
CREATE DATABASE lms_db OWNER stayer;
GRANT ALL PRIVILEGES ON DATABASE lms_db TO stayer;
```

##### 3. Настраиваем схему `public`
```
ALTER DATABASE lms_db OWNER TO stayer;
ALTER SCHEMA public OWNER TO stayer;
GRANT ALL ON SCHEMA public TO stayer;
```

##### 4. Проверяем, что пользователь имеет права
```
\dn+
\l
```
Вы должны увидеть, что:
* владелец схемы `public` — `stayer`
* владелец базы данных — `stayer`

#### 🗃️ Настройка Redis (для Celery)
Redis используется как брокер сообщений для Celery.

##### 1. Установите Redis
Для Ubuntu/Linux:
```
sudo apt update
sudo apt install redis-server
```

Для других ОС следуйте официальной документации Redis.

##### 2. Запустите Redis
```
redis-server
```

Проверьте, что Redis работает (по умолчанию на порту 6379).

#### ⚙️ Настройки Django
Откройте `settings.py` и проверьте блок `DATABASES`:
```
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

Добавьте настройки для Celery (если их ещё нет):
```
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
```

#### 🧱 Миграции
Применяем миграции:
```
python manage.py makemigrations
python manage.py migrate
```
Если видите ошибку `нет доступа к схеме public` — убедитесь, что владелец базы данных и схемы совпадает с пользователем, указанным в `settings.py`.

#### 👤 Создание суперпользователя
```
python manage.py createsuperuser
```

#### ▶️ Запуск сервера
```
python manage.py runserver
```
Откройте в браузере:
```
http://127.0.0.1:8000/
```

#### 🕒 Запуск Celery
Для обработки асинхронных задач запустите worker (в отдельном терминале):
```
celery -A config worker -l info
```

Для периодических задач (если используются, например, через celery beat scheduler) запустите beat:
```
celery -A config beat -l info
```

#### 🐳 Docker
Docker — это платформа для контейнеризации приложений, которая позволяет упаковывать проект со всеми зависимостями в изолированные контейнеры. Это упрощает развертывание, обеспечивает consistency окружения и облегчает масштабирование. В этом проекте Docker используется для запуска Django-приложения вместе с PostgreSQL, Redis и Celery в контейнерах. Для оркестрации нескольких контейнеров применяется Docker Compose.

##### 1. Установите Docker
- Скачайте и установите Docker Desktop (для Windows/Mac) или Docker Engine (для Linux) с официального сайта: https://www.docker.com/.
- Убедитесь, что Docker установлен и запущен: `docker --version`.

##### 2. Создайте Dockerfile (если его ещё нет)
В корне проекта создайте файл `Dockerfile` со следующим содержимым:
```
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

Этот файл определяет образ для Django-приложения: базируется на Python 3.13, устанавливает зависимости и запускает сервер.

##### 3. Создайте docker-compose.yml (если его ещё нет)
В корне проекта создайте файл `docker-compose.yml` для оркестрации сервисов:
```
version: '3.9'

services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: lms_db
      POSTGRES_USER: stayer
      POSTGRES_PASSWORD: your_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7
    ports:
      - "6379:6379"

  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    environment:
      - DATABASE_URL=postgres://stayer:your_password@db:5432/lms_db
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0

  celery_worker:
    build: .
    command: celery -A config worker -l info
    volumes:
      - .:/app
    depends_on:
      - db
      - redis
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0

  celery_beat:
    build: .
    command: celery -A config beat -l info
    volumes:
      - .:/app
    depends_on:
      - db
      - redis
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0

volumes:
  postgres_data:
```

Этот файл запускает:
- PostgreSQL (db)
- Redis
- Django сервер (web)
- Celery worker
- Celery beat

Обновите `settings.py`, чтобы использовать переменные окружения (например, для DATABASES и CELERY).

##### 4. Запуск с Docker Compose
- Соберите и запустите контейнеры: `docker-compose up -d --build`
- Примените миграции: `docker-compose exec web python manage.py migrate`
- Создайте суперпользователя: `docker-compose exec web python manage.py createsuperuser`
- Остановите: `docker-compose down`

Приложение будет доступно по `http://localhost:8000/`. Для production используйте Gunicorn вместо runserver и настройте volumes для persistent data.

#### Новые функции
* Валидация ссылок : В уроках разрешены только YouTube-ссылки.
* Подписки : Эндпоинт /api/subscriptions/ для toggle подписки (POST с course_id).
* Пагинация : Для списков курсов и уроков (page_size=10).
* Тесты : Покрытие CRUD для уроков, подписок и других эндпоинтов (запустить pytest --cov).
* Celery: Интеграция для отложенных и периодических задач (например, отправка уведомлений о обновлениях курсов).

#### ✅ Тестирование (Pytest)
Если используете pytest, запустите тесты:
```
pytest --cov
```
Для удобства добавьте файл `pytest.ini` в корень проекта:
```
[pytest]
DJANGO_SETTINGS_MODULE = config.settings
python_files = tests.py test_*.py *_tests.py
```
---

## CI/CD и Развертывание на сервере

Этот проект настроен на автоматическое тестирование и развертывание с использованием GitHub Actions и Docker.

### 1. Первоначальная настройка сервера

Для работы CI/CD вам понадобится удаленный сервер (например, Ubuntu 22.04).

1.  **Установите Docker:**
    ```bash
    sudo apt update
    sudo apt install docker.io
    sudo systemctl start docker
    sudo systemctl enable docker
    ```

2.  **Установите Docker Compose:**
    ```bash
    sudo apt install docker-compose
    ```

3.  **Добавьте пользователя в группу Docker** (чтобы не использовать `sudo`):
    ```bash
    sudo usermod -aG docker $USER
    # После этого перелогиньтесь на сервере
    ```

4.  **Создайте директорию для проекта:**
    ```bash
    mkdir -p /home/ваш_пользователь/projects/ваш_проект
    cd /home/ваш_пользователь/projects/ваш_проект
    ```

5.  **Клонируйте репозиторий (только для первого раза):**
    ```bash
    git clone [https://github.com/ваш_логин/ваш_репозиторий.git](https://github.com/ваш_логин/ваш_репозиторий.git) .
    ```

6.  **Создайте первичный `.env` файл:**
    Скопируйте `.env.example` и заполните его реальными данными.
    ```bash
    cp .env.example .env
    nano .env 
    # Заполните SECRET_KEY, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
    # ALLOWED_HOSTS должен включать IP вашего сервера
    ```

### 2. Настройка секретов в GitHub

Для работы GitHub Actions необходимо настроить "Secrets" в вашем репозитории (`Settings` -> `Secrets and variables` -> `Actions`).

Создайте следующие **Repository secrets**:

* `SERVER_HOST`: IP-адрес вашего удаленного сервера.
* `SERVER_USER`: Имя пользователя для SSH-подключения (например, `root` или `ubuntu`).
* `SSH_PRIVATE_KEY`: Приватный SSH-ключ для доступа к серверу (содержимое файла `~/.ssh/id_rsa`).
* `SSH_PASSPHRASE`: (Опционально) Пароль от вашего `SSH_PRIVATE_KEY`, если он есть.

* `DOCKER_USERNAME`: Ваш логин на [Docker Hub](https://hub.docker.com/).
* `DOCKER_PASSWORD`: Ваш пароль или Access Token от Docker Hub.
* `DOCKER_REPO`: Название репозитория на Docker Hub, куда будут загружаться образы (например, `my-django-app`).

* `SECRET_KEY`: Секретный ключ Django.
* `POSTGRES_DB`: Имя базы данных.
* `POSTGRES_USER`: Имя пользователя базы данных.
* `POSTGRES_PASSWORD`: Пароль пользователя базы данных.

### 3. Процесс CI/CD

1.  **Push в репозиторий**: Каждый `push` в ветку `main` (или `develop`, как настроено в `main.yml`) автоматически запускает workflow.
2.  **Test**: Запускается job `test`, который устанавливает зависимости и выполняет `python manage.py test` в изолированном окружении с тестовой БД.
3.  **Build**: В случае успеха тестов, job `deploy` собирает Docker-образы для `web` и `nginx` и загружает их в ваш Docker Hub.
4.  **Deploy**: Workflow подключается к вашему серверу по SSH.
5.  На сервере создается актуальный `.env` файл из GitHub Secrets.
6.  `docker-compose pull` загружает новые образы с Docker Hub.
7.  `docker-compose up -d --build` перезапускает сервисы с новыми образами.
8.  Выполняются команды `migrate` и `collectstatic` внутри запущенного `web` контейнера.
9.  Ваше приложение обновлено и доступно по IP-адресу сервера.

#### 🧩 Полезные команды
```
# Проверка списка миграций
python manage.py showmigrations

# Просмотр подключённых приложений
python manage.py listapps

# Проверка прав пользователя PostgreSQL
sudo -u postgres psql -c "\du+"

# Проверка схем
sudo -u postgres psql -c "\dn+"
```

#### 🪪 Автор
Стюхин Андрей

#### 📝 Лицензия
Проект распространяется под лицензией MIT.
```