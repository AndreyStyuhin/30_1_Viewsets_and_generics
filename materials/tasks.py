from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from materials.models import Subscription


@shared_task
def send_course_update_notification(course_id, course_title):
    """
    Отправляет email-уведомления подписчикам курса.
    """
    try:
        # Находим всех подписчиков этого курса
        subscriptions = Subscription.objects.filter(course_id=course_id)

        # Собираем email-адреса, исключая пустые
        user_emails = [sub.user.email for sub in subscriptions if sub.user.email]

        if user_emails:
            subject = f'Обновление курса: {course_title}'
            message = f'Материалы курса "{course_title}", на который вы подписаны, были обновлены.'

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=user_emails,
                fail_silently=False,
            )
            return f"Уведомления для курса '{course_title}' отправлены {len(user_emails)} пользователям."
        else:
            return f"Для курса '{course_title}' нет подписчиков с email."

    except Exception as e:
        # Логгирование ошибки, если что-то пошло не так
        print(f"Ошибка при отправке уведомлений для курса {course_id}: {e}")
        return f"Ошибка отправки для курса {course_id}."