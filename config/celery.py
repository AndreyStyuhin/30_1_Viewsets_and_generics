import os
from celery import Celery

# Установите переменную окружения Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

# Используйте префикс 'CELERY_' для всех настроек Celery из settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматическое обнаружение задач из всех установленных приложений Django
app.autodiscover_tasks()