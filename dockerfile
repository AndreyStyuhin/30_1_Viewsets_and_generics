# 1. Базовый образ
FROM python:3.10-slim-buster

# Установка системных зависимостей
RUN apt-get update \
    && apt-get install -y build-essential libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Установка переменных окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Создание рабочей директории
WORKDIR /app

# Установка зависимостей Python
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Копирование исходного кода проекта
COPY . .

# Сбор статики (этот шаг также будет в Nginx, но полезно иметь здесь)
# Если у вас статика в Django, раскомментируйте:
# RUN python manage.py collectstatic --noinput

# Пользователь без root прав
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# Gunicorn будет запущен через docker-compose