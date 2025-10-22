from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta

from materials.models import Course, Lesson, Subscription
from materials.serializers import CourseSerializer, LessonSerializer
from materials.paginators import MaterialsPagination
from materials.tasks import send_course_update_notification  # <--- TASK 2


class IsModerator(BasePermission):
    """
    Права доступа для группы 'moderators'.
    """

    def has_permission(self, request, view):
        return request.user.groups.filter(name='moderators').exists()


class IsOwner(BasePermission):
    """
    Права доступа для владельца объекта.
    """

    def has_object_permission(self, request, view, obj):
        # Проверяем, есть ли у объекта атрибут 'owner'
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        return False


# --- End Permissions ---


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    pagination_class = MaterialsPagination

    def get_permissions(self):
        """
        Права доступа:
        - Модераторы (IsModerator) могут всё (list, retrieve, update).
        - Владельцы (IsOwner) могут всё со своими объектами.
        - Создавать (create) может любой аутентифицированный пользователь.
        - Удалять (destroy) может только владелец (не модератор) (согласно тестам).
        """
        if self.action == 'create':
            self.permission_classes = [IsAuthenticated]
        elif self.action == 'destroy':
            self.permission_classes = [IsAuthenticated, IsOwner]
        elif self.action in ['update', 'partial_update', 'retrieve']:
            self.permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        else:  # list
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        """
        - Модераторы видят все курсы.
        - Обычные пользователи видят только свои курсы.
        """
        user = self.request.user
        if user.groups.filter(name='moderators').exists():
            return Course.objects.all()
        return Course.objects.filter(owner=user)

    def perform_create(self, serializer):
        """Присваиваем владельца при создании."""
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):  # <--- TASK 2
        """
        Переопределяем обновление для отправки уведомлений
        при обновлении самого КУРСА.
        """
        course = self.get_object()

        # Проверка 4-часового интервала ПЕРЕД сохранением
        can_notify = (timezone.now() - course.last_updated_at) > timedelta(hours=4)

        # Сохраняем изменения курса и обновляем время вручную
        updated_course = serializer.save(last_updated_at=timezone.now())

        if can_notify:
            send_course_update_notification.delay(updated_course.id, updated_course.title)


class LessonListCreateView(generics.ListCreateAPIView):
    serializer_class = LessonSerializer
    pagination_class = MaterialsPagination
    permission_classes = [IsAuthenticated]  # Создавать может любой

    def get_queryset(self):
        """
        - Модераторы видят все уроки.
        - Обычные пользователи видят только свои уроки.
        """
        user = self.request.user
        if user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)

    def perform_create(self, serializer):
        """Присваиваем владельца при создании."""
        lesson = serializer.save(owner=self.request.user)

        # При создании урока также обновляем курс (Доп. задание)
        course = lesson.course
        if (timezone.now() - course.last_updated_at) > timedelta(hours=4):
            send_course_update_notification.delay(course.id, course.title)

        course.last_updated_at = timezone.now()
        course.save()


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LessonSerializer

    def get_permissions(self):
        """
        - Модераторы: retrieve, update.
        - Владельцы: retrieve, update, destroy.
        """
        if self.request.method == 'DELETE':
            self.permission_classes = [IsAuthenticated, IsOwner]
        else:
            self.permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        return super().get_permissions()

    def get_queryset(self):
        """
        - Модераторы видят все уроки.
        - Обычные пользователи видят только свои уроки.
        """
        user = self.request.user
        if user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)

    def perform_update(self, serializer):  # <--- TASK 2 (Доп. задание)
        """
        Переопределяем обновление УРОКА, чтобы уведомить подписчиков КУРСА.
        """
        # Сохраняем урок
        lesson = serializer.save()
        course = lesson.course

        # Проверка 4-часового интервала
        if (timezone.now() - course.last_updated_at) > timedelta(hours=4):
            # Отправляем уведомление
            send_course_update_notification.delay(course.id, course.title)

        # Обновляем время у курса (т.к. обновление урока = обновление курса)
        course.last_updated_at = timezone.now()
        course.save()


class SubscriptionToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Переключатель подписки (POST-запрос).
        Ожидает {'course_id': ID_курса} в теле запроса.
        """
        user = request.user
        course_id = request.data.get('course_id')

        if not course_id:
            return Response({'error': 'Не указан course_id'}, status=status.HTTP_400_BAD_REQUEST)

        course = get_object_or_404(Course, id=course_id)

        # Пытаемся найти подписку
        subscription, created = Subscription.objects.get_or_create(user=user, course=course)

        if created:
            message = 'подписка добавлена'
        else:
            # Если найдена, удаляем
            subscription.delete()
            message = 'подписка удалена'

        return Response({'message': message}, status=status.HTTP_200_OK)