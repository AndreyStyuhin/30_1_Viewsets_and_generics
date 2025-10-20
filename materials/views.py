from rest_framework import viewsets, generics, permissions, status
from materials.models import Course, Lesson, Subscription
from materials.paginators import MaterialsPagination
from materials.serializers import CourseSerializer, LessonSerializer
from users.permissions import IsModer, IsOwner
from materials.permissions import IsModerOrIsOwner
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission, IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes, OpenApiResponse, inline_serializer
from rest_framework import serializers

# Раскомментировать --- COURSE VIEWSET ---

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all().order_by('id')
    serializer_class = CourseSerializer
    pagination_class = MaterialsPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='moderators').exists():
            return Course.objects.all()
        else:
            return Course.objects.filter(owner=user)

    def get_permissions(self):
        if self.action in ['list', 'create']:
            return [permissions.IsAuthenticated()]
        if self.action in ['retrieve', 'update', 'partial_update']:
            return [permissions.IsAuthenticated(), IsModerOrIsOwner()]
        if self.action == 'destroy':
            return [permissions.IsAuthenticated(), IsOwner()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @extend_schema(
        summary="Список курсов",
        description="Возвращает курсы текущего пользователя или все для модераторов (с пагинацией).",
        responses={
            200: CourseSerializer(many=True),
            401: OpenApiResponse(description="Unauthorized - Требуется аутентификация"),
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Создание курса",
        description="Создает новый курс. Текущий пользователь автоматически назначается владельцем.",
        responses={
            201: CourseSerializer,
            400: OpenApiResponse(description="Bad Request - Неверные данные"),
            401: OpenApiResponse(description="Unauthorized - Требуется аутентификация"),
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Получение курса",
        description="Возвращает детальную информацию о курсе. Доступно модераторам и владельцу.",
        responses={
            200: CourseSerializer,
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Forbidden - Нет прав доступа"),
            404: OpenApiResponse(description="Not Found"),
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Обновление курса (PUT)",
        description="Полностью обновляет курс. Доступно модераторам и владельцу.",
        responses={200: CourseSerializer, 401: OpenApiResponse(description="Unauthorized"),
                   403: OpenApiResponse(description="Forbidden")}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Частичное обновление курса (PATCH)",
        description="Частично обновляет курс. Доступно модераторам и владельцу.",
        responses={200: CourseSerializer, 401: OpenApiResponse(description="Unauthorized"),
                   403: OpenApiResponse(description="Forbidden")}
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        summary="Удаление курса",
        description="Удаляет курс. Доступно только владельцу.",
        responses={
            204: OpenApiResponse(description="No Content - Курс успешно удален"),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Forbidden - Только владелец может удалить"),
            404: OpenApiResponse(description="Not Found"),
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


# --- LESSON VIEWS ---

@extend_schema(
    summary="Список и создание уроков",
    description="Возвращает уроки текущего пользователя или все для модераторов (GET). Создает новый урок (POST).",
    responses={
        200: LessonSerializer(many=True),
        201: LessonSerializer,
        401: OpenApiResponse(description="Unauthorized"),
    }
)
class LessonListCreateView(generics.ListCreateAPIView):
    serializer_class = LessonSerializer
    pagination_class = MaterialsPagination
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.groups.filter(name='moderators').exists():
            return Lesson.objects.all().order_by('id')
        return Lesson.objects.filter(owner=self.request.user).order_by('id')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


@extend_schema(
    summary="Просмотр, изменение и удаление урока",
    description="Детальный просмотр (GET), обновление (PUT/PATCH) и удаление (DELETE) урока. Доступно модераторам и владельцу.",
    responses={
        200: LessonSerializer,
        204: OpenApiResponse(description="No Content - Урок удален (DELETE)"),
        401: OpenApiResponse(description="Unauthorized"),
        403: OpenApiResponse(description="Forbidden - Нет прав доступа"),
        404: OpenApiResponse(description="Not Found"),
    }
)
class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method in ('GET', 'PUT', 'PATCH'):
            return [permissions.IsAuthenticated(), IsModer | IsOwner]
        if self.request.method == 'DELETE':
            return [permissions.IsAuthenticated(), IsOwner()]
        return [permissions.IsAuthenticated()]


# --- SUBSCRIPTION VIEW ---

@extend_schema(
    summary="Включение/отключение подписки на курс",
    description="Переключает (включает/отключает) подписку текущего пользователя на указанный курс.",
    request=inline_serializer(
        name='SubscriptionToggleRequest',
        fields={'course_id': serializers.IntegerField(help_text="ID курса для подписки/отписки.")}
    ),
    responses={
        200: OpenApiResponse(
            response=inline_serializer(name='SubscriptionToggleResponse', fields={'message': serializers.CharField()}),
            description="Состояние подписки изменено ('подписка добавлена'/'подписка удалена')"
        ),
        400: OpenApiResponse(description="Bad Request - Не указан course_id"),
        401: OpenApiResponse(description="Unauthorized"),
        404: OpenApiResponse(description="Not Found - Курс не найден"),
    }
)
class SubscriptionToggleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get('course_id')
        if not course_id:
            return Response({'error': 'course_id required'}, status=status.HTTP_400_BAD_REQUEST)
        course = get_object_or_404(Course, id=course_id)
        sub = Subscription.objects.filter(user=user, course=course)
        if sub.exists():
            sub.delete()
            message = 'подписка удалена'
        else:
            Subscription.objects.create(user=user, course=course)
            message = 'подписка добавлена'
        return Response({'message': message}, status=status.HTTP_200_OK)


class IsModerOrOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return IsModer().has_object_permission(request, view, obj) or IsOwner().has_object_permission(request, view,
                                                                                                      obj)