# ФАЙЛ: materials/views.py

from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
# Добавлен @extend_schema_field для сериализатора
from drf_spectacular.utils import extend_schema, OpenApiParameter, inline_serializer, extend_schema_field
from materials.models import Course, Lesson, Subscription
from materials.serializers import CourseSerializer, LessonSerializer
from materials.paginators import MaterialsPagination
from materials.permissions import IsOwner, IsModerator
from rest_framework import serializers  # для inline_serializer


class CourseViewSet(viewsets.ModelViewSet):
    """
    (Задание 1)
    ViewSet для управления курсами.
    Позволяет создавать, просматривать, редактировать и удалять курсы.
    - Обычные пользователи: видят, редактируют, удаляют только *свои* курсы.
    - Модераторы: видят и редактируют *все* курсы, но не могут их удалять.
    """
    serializer_class = CourseSerializer
    pagination_class = MaterialsPagination

    def get_queryset(self):
        """
        Модераторы видят все курсы,
        обычные пользователи - только свои.
        """
        # --- ИСПРАВЛЕНИЕ (Warning 1): Проверка на AnonymousUser для drf-spectacular ---
        if not self.request.user.is_authenticated:
            return Course.objects.none()
        # ---

        if self.request.user.groups.filter(name='moderators').exists():
            return Course.objects.all().order_by('id')
        return Course.objects.filter(owner=self.request.user).order_by('id')

    def get_permissions(self):
        """
        Установка прав доступа в зависимости от действия.
        - destroy: Только владелец (IsOwner)
        - update/partial_update/retrieve: Владелец (IsOwner) ИЛИ Модератор (IsModerator)
        - create/list: Любой аутентифицированный пользователь (IsAuthenticated)
        """
        if self.action == 'destroy':
            permission_classes = [IsAuthenticated, IsOwner]
        elif self.action in ['update', 'partial_update', 'retrieve']:
            permission_classes = [IsAuthenticated, IsOwner | IsModerator]
        else:  # 'list', 'create'
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """Присваиваем владельца при создании курса."""
        serializer.save(owner=self.request.user)


class LessonListCreateAPIView(generics.ListCreateAPIView):
    """
    (Задание 1)
    API-эндпоинт для просмотра списка и создания уроков.
    - POST: Создает новый урок (владелец присваивается автоматически).
    - GET: Возвращает список уроков, принадлежащих текущему пользователю (или всех, если модератор).
    """
    serializer_class = LessonSerializer
    pagination_class = MaterialsPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Модераторы видят все уроки,
        обычные пользователи - только свои.
        """
        # --- ИСПРАВЛЕНИЕ (Warning 1): Проверка на AnonymousUser для drf-spectacular ---
        if not self.request.user.is_authenticated:
            return Lesson.objects.none()
        # ---

        if self.request.user.groups.filter(name='moderators').exists():
            return Lesson.objects.all().order_by('id')
        return Lesson.objects.filter(owner=self.request.user).order_by('id')

    def perform_create(self, serializer):
        """Присваиваем владельца при создании урока."""
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    (Задание 1)
    API-эндпоинт для просмотра, редактирования и удаления урока.
    - GET: Просмотр урока (владелец или модератор).
    - PUT/PATCH: Редактирование урока (владелец или модератор).
    - DELETE: Удаление урока (только владелец).
    """
    serializer_class = LessonSerializer

    def get_queryset(self):
        """
        Модераторы видят все уроки,
        обычные пользователи - только свои.
        """
        # --- ИСПРАВЛЕНИЕ (Warning 1): Проверка на AnonymousUser для drf-spectacular ---
        if not self.request.user.is_authenticated:
            return Lesson.objects.none()
        # ---

        if self.request.user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=self.request.user)

    def get_permissions(self):
        """
        Установка прав доступа в зависимости от действия.
        - destroy: Только владелец (IsOwner)
        - update/partial_update/retrieve: Владелец (IsOwner) ИЛИ Модератор (IsModerator)
        """
        # --- ИСПРАВЛЕНИЕ (Fatal Error): Заменено self.action на self.request.method ---
        if self.request.method == 'DELETE':
            permission_classes = [IsAuthenticated, IsOwner]
        else:  # 'GET', 'PUT', 'PATCH'
            permission_classes = [IsAuthenticated, IsOwner | IsModerator]
        # ---
        return [permission() for permission in permission_classes]


@extend_schema(
    summary="(Задание 1) Управление подпиской на курс (Toggle)",
    description="""
    Создает или удаляет подписку пользователя на указанный курс.
    - Если подписки нет - создает.
    - Если подписка есть - удаляет.
    Возвращает статус 201 (Created) или 204 (No Content).
    """,
    request=inline_serializer(
        name='SubscriptionToggleRequest',
        fields={'course_id': serializers.IntegerField(help_text="ID курса для подписки/отписки")}
    ),
    responses={
        201: inline_serializer(name='SubscriptionCreated', fields={'message': serializers.CharField()}),
        204: 'Подписка успешно удалена (No Content).',
        400: inline_serializer(name='SubscriptionError400', fields={'error': serializers.CharField()}),
        404: inline_serializer(name='SubscriptionError404', fields={'error': serializers.CharField()})
    }
)
class SubscriptionAPIView(generics.GenericAPIView):
    """
    API-эндпоинт для управления подписками (вкл/выкл).
    Принимает POST-запрос с 'course_id'.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = None  # Только для схемы

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get('course_id')

        if not course_id:
            return Response({'error': 'Необходимо указать course_id.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return Response({'error': 'Курс не найден.'}, status=status.HTTP_404_NOT_FOUND)

        # Ищем существующую подписку
        subscription, created = Subscription.objects.get_or_create(user=user, course=course)

        if created:
            # Если подписка была создана
            return Response({'message': f'Вы успешно подписались на курс "{course.title}".'},
                            status=status.HTTP_201_CREATED)
        else:
            # Если подписка уже существовала, удаляем ее
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)