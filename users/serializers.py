from rest_framework import serializers
from users.models import User, Payment
from materials.models import Course, Lesson  # Нужны для PrimaryKeyRelatedField


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'phone',
            'city',
            'avatar',
            'password'
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }
        # Убедитесь, что здесь нет полей, которые вы пытаетесь обновить
        # read_only_fields = ('is_active', )


class PaymentSerializer(serializers.ModelSerializer):
    """
    (Задание 1) Сериализатор для *просмотра* списка платежей.
    Показывает все поля, включая сгенерированные Stripe.
    """
    user = serializers.PrimaryKeyRelatedField(read_only=True, help_text="ID пользователя")
    course = serializers.PrimaryKeyRelatedField(read_only=True, help_text="ID оплаченного курса")
    lesson = serializers.PrimaryKeyRelatedField(read_only=True, help_text="ID оплаченного урока")

    # Поля, добавленные в Task 2 (Stripe)
    payment_link = serializers.URLField(read_only=True, help_text="Ссылка на страницу оплаты (генерируется Stripe)")
    is_paid = serializers.BooleanField(read_only=True, help_text="Статус оплаты (обновляется Stripe)")
    stripe_session_id = serializers.CharField(read_only=True, help_text="ID сессии в Stripe")

    amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True, help_text="Сумма")
    payment_method = serializers.CharField(read_only=True, help_text="Метод оплаты")
    payment_date = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Payment
        fields = '__all__'


class PaymentCreateSerializer(serializers.ModelSerializer):
    """
    (Задание 2) Специальный сериализатор для *создания* платежа.
    Требует только ID курса, остальное генерируется автоматически.
    """
    course = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(),
        required=True,
        write_only=True,
        help_text="ID курса для покупки"
    )

    # Поля, которые будут возвращены в ответе
    payment_link = serializers.URLField(read_only=True)
    stripe_session_id = serializers.CharField(read_only=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Payment
        # Указываем поля, которые используются/возвращаются
        fields = ('course', 'payment_link', 'stripe_session_id', 'amount', 'id')

    def validate_course(self, course):
        # Проверим, что у курса есть цена
        if not course.price or course.price <= 0:
            raise serializers.ValidationError("У этого курса не указана цена или он бесплатный.")

        # (Опционально) Проверим, не покупал ли пользователь этот курс ранее
        user = self.context['request'].user
        if Payment.objects.filter(user=user, course=course, is_paid=True).exists():
            raise serializers.ValidationError("Вы уже приобрели этот курс.")

        return course