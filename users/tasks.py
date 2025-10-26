from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


@shared_task
def block_inactive_users():
    """
    Блокирует пользователей, которые не заходили более 1 месяца (30 дней).
    """
    # Определяем дату, ранее которой пользователи считаются неактивными
    cutoff_date = timezone.now() - timedelta(days=30)

    # Находим пользователей, которые:
    # 1. Активны (is_active=True)
    # 2. Не являются суперпользователями (is_superuser=False)
    # 3. Заходили последний раз *раньше*, чем cutoff_date (т.е. более 30 дней назад)

    users_to_block = User.objects.filter(
        is_active=True,
        is_superuser=False,
        last_login__lt=cutoff_date
    )

    # Блокируем их
    count = users_to_block.update(is_active=False)

    logger.info(f"Заблокировано {count} пользователей из-за неактивности (последний вход до {cutoff_date.date()}).")
    return f"Blocked {count} inactive users."