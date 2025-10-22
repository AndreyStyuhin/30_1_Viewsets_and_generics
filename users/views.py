# ФАЙЛ: users/views.py

from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers  # для inline_serializer

from users.models import User, Payment
from materials.models import Course  # Нужен для создания платежа
from users.serializers import UserSerializer, PaymentSerializer, PaymentCreateSerializer
from users.services import create_stripe_product, create_stripe_price, create_stripe_session, retrieve_stripe_session


class UserViewSet(viewsets.ModelViewSet):
    """
    (Задание 1)
    ViewSet для управления пользователями (Профили).
    Позволяет просматривать, редактировать и создавать профили.
    Обычные пользователи могут видеть и редактировать только свой профиль.
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_permissions(self):
        """
        - Создание (create) доступно всем (AllowAny)
        - Просмотр списка (list) только админу (IsAdminUser)
        - Остальное (retrieve, update, destroy) - только владельцу профиля
        """
        if self.action == 'create':
            self.permission_classes = [AllowAny]
        elif self.action == 'list':
            self.permission_classes = [IsAuthenticated, IsAdminUser]
        elif self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        """
        Пользователи могут видеть/редактировать только свой профиль.
        (Админ видит всех)
        """
        if self.request.user.is_superuser:
            return User.objects.all()

        # --- ИСПРАВЛЕНИЕ (Warning 1): Проверка на AnonymousUser ---
        if self.request.user.is_authenticated:
            return User.objects.filter(pk=self.request.user.pk)
        return User.objects.none()
        # ---


class PaymentListAPIView(generics.ListAPIView):
    """
    (Задание 1)
    API-эндпоинт для просмотра списка платежей ТЕКУЩЕГО пользователя.
    Позволяет фильтровать по курсу, уроку и способу оплаты.
    """
    serializer_class = PaymentSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter,)
    filterset_fields = ('course', 'lesson', 'payment_method',)
    ordering_fields = ('payment_date',)
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Пользователи видят только свои платежи."""
        # --- ИСПРАВЛЕНИЕ (Warning 1): Проверка на AnonymousUser ---
        if not self.request.user.is_authenticated:
            return Payment.objects.none()
        # ---
        return Payment.objects.filter(user=self.request.user)


@extend_schema(
    summary="(Задание 2) Создание сессии оплаты (Stripe)",
    # ... (остальная часть @extend_schema)
)
class PaymentCreateAPIView(generics.CreateAPIView):
    """
    (ЗАДАНИЕ 2)
    API-эндпоинт для создания платежа и получения ссылки на оплату Stripe.
    """
    serializer_class = PaymentCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # ... (логика Stripe)
        course = serializer.validated_data['course']
        user = self.request.user

        try:
            stripe_product = create_stripe_product(name=course.title)
            if not stripe_product:
                raise Exception("Не удалось создать продукт в Stripe.")

            amount_in_cents = int(course.price * 100)
            stripe_price = create_stripe_price(
                product_id=stripe_product.id,
                amount=amount_in_cents
            )
            if not stripe_price:
                raise Exception("Не удалось создать цену в Stripe.")

            stripe_session = create_stripe_session(price_id=stripe_price.id)
            if not stripe_session:
                raise Exception("Не удалось создать сессию в Stripe.")

            serializer.save(
                user=user,
                amount=course.price,
                payment_method='transfer',
                stripe_session_id=stripe_session.id,
                payment_link=stripe_session.url
            )

        except Exception as e:
            raise serializers.ValidationError(f"Ошибка при создании платежа Stripe: {e}")


@extend_schema(
    summary="(Задание 2 - Бонус) Проверка статуса платежа",
    # ... (остальная часть @extend_schema)
)
class PaymentRetrieveAPIView(generics.RetrieveAPIView):
    """
    (ЗАДАНИЕ 2 - БОНУС)
    API-эндпоинт для проверки статуса платежа в Stripe по PK платежа в нашей БД.
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Пользователи видят только свои платежи."""
        # --- ИСПРАВЛЕНИЕ (Warning 1): Проверка на AnonymousUser ---
        if not self.request.user.is_authenticated:
            return Payment.objects.none()
        # ---
        return Payment.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        payment = self.get_object()

        if not payment.stripe_session_id:
            return Response({'error': 'Этот платеж не был обработан Stripe.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            session = retrieve_stripe_session(payment.stripe_session_id)

            if not session:
                return Response({'error': 'Не удалось получить сессию из Stripe.'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            if session.payment_status == 'paid':
                if not payment.is_paid:
                    payment.is_paid = True
                    payment.save()

            return Response(self.get_serializer(payment).data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': f'Ошибка при проверке статуса: {e}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Views для success/cancel
class PaymentSuccessView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    @extend_schema(summary="(Заглушка) Страница успеха Stripe", description="Заглушка для Stripe success_url.")
    def get(self, request, *args, **kwargs):
        return Response({'message': 'Оплата прошла успешно!'}, status=status.HTTP_200_OK)


class PaymentCancelView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    @extend_schema(summary="(Заглушка) Страница отмены Stripe", description="Заглушка для Stripe cancel_url.")
    def get(self, request, *args, **kwargs):
        return Response({'message': 'Оплата отменена.'}, status=status.HTTP_200_OK)