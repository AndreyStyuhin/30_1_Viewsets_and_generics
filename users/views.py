from rest_framework import generics, status
from rest_framework.response import Response
from users.models import User
from users.serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserProfileSerializer
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