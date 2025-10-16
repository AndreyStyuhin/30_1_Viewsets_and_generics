from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from users.models import User, Payment
from users.permissions import IsOwner
from users.serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserProfileSerializer,
    PaymentSerializer
)
from users.serializers import PublicUserSerializer
from rest_framework import generics, permissions, status
from users.models import User


class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = PublicUserSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserRetrieveView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    def get_serializer_class(self):
        user = self.request.user
        obj = self.get_object()
        if obj == user:
            return UserProfileSerializer
        return PublicUserSerializer


class UserProfileUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class UserDestroyView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
    # разрешаем удаление только своему аккаунту
        obj = self.get_object()
        if obj != request.user:
            return Response({'detail': 'You can delete only your account.'}, status=403)
        return super().delete(request, *args, **kwargs)


class PaymentListView(generics.ListAPIView):
    """Список платежей с фильтрами и сортировкой"""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['course', 'lesson', 'payment_method']
    ordering_fields = ['payment_date']