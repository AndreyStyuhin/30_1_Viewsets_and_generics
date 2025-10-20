from rest_framework import serializers
from users.models import User, Payment


class PaymentSerializer(serializers.ModelSerializer):
    """Стандартный сериализатор для просмотра списка платежей."""

    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ('user', 'payment_date', 'amount', 'stripe_session_id', 'payment_link', 'is_paid',
                            'payment_method')


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра пользователя"""
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'city', 'avatar', 'payments']
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
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'city', 'avatar', 'payments']
        read_only_fields = ['id', 'email']

class PublicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'avatar', 'city']
        read_only_fields = ['id', 'email']


class PaymentCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для инициирования платежа через POST-запрос."""

    class Meta:
        model = Payment
        fields = ('course', 'lesson')
        extra_kwargs = {
            'course': {'required': False},
            'lesson': {'required': False},
        }

    def validate(self, data):
        # Проверка, что оплачивается либо курс, либо урок, но не оба
        course = data.get('course')
        lesson = data.get('lesson')

        if course and lesson:
            raise serializers.ValidationError("Нельзя оплачивать одновременно курс и урок.")
        if not (course or lesson):
            raise serializers.ValidationError("Необходимо указать курс или урок для оплаты.")

        # Установка способа оплаты как 'TRANSFER' (для Stripe)
        data['payment_method'] = Payment.PaymentMethod.TRANSFER
        return data