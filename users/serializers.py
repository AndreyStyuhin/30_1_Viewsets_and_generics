from rest_framework import serializers
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра пользователя"""

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'city', 'avatar']
        read_only_fields = ['id', 'email']


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания пользователя"""
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'phone', 'city', 'avatar']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для редактирования профиля"""

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'city', 'avatar']
        read_only_fields = ['id', 'email']