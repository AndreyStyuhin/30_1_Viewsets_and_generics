from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from users.models import User, Payment
from users.serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserProfileSerializer,
    PaymentSerializer
)


class UserCreateView(generics.CreateAPIView):
    """Создание нового пользователя (регистрация)"""
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer


class UserListView(generics.ListAPIView):
    """Список всех пользователей"""
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserRetrieveView(generics.RetrieveAPIView):
    """Просмотр профиля пользователя"""
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserProfileUpdateView(generics.RetrieveUpdateAPIView):
    """Редактирование профиля пользователя"""
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer

    def get_object(self):
        """
        Можно вернуть текущего пользователя
        Пока возвращаем по pk из URL
        """
        return super().get_object()


class UserDestroyView(generics.DestroyAPIView):
    """Удаление пользователя"""
    queryset = User.objects.all()
    serializer_class = UserSerializer


class PaymentListView(generics.ListAPIView):
    """Список платежей с фильтрами и сортировкой"""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['course', 'lesson', 'payment_method']
    ordering_fields = ['payment_date']