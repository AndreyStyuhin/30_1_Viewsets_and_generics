# users/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Payment
from .serializers import PaymentSerializer, PaymentCreateSerializer
from .services import (
    create_stripe_product, create_stripe_price,
    create_stripe_checkout_session, retrieve_stripe_session
)
from materials.models import Course, Lesson
from django.shortcuts import get_object_or_404  # Может понадобиться, если не используется get_queryset().get(pk=pk)


class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления платежами.
    Предоставляет CRUD операции и custom-экшены для инициирования и проверки статуса оплаты через Stripe.
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]  # Базовая аутентификация
    filterset_fields = ('course', 'lesson', 'payment_method')
    ordering_fields = ('payment_date',)

    def get_serializer_class(self):
        if self.action == 'create_payment':
            return PaymentCreateSerializer
        return PaymentSerializer

    def get_queryset(self):
        # Ограничение доступа: Пользователь видит только свои платежи
        if self.request.user.is_staff or self.request.user.is_superuser or self.request.user.groups.filter(
                name='moderators').exists():
            return self.queryset
        return self.queryset.filter(user=self.request.user)

    @action(detail=False, methods=['post'], url_path='create-payment',
            serializer_class=PaymentCreateSerializer,
            description="Инициировать платеж через Stripe. Создает продукт, цену и сессию. Возвращает ссылку на оплату.")
    def create_payment(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = request.user
        course = data.get('course')
        lesson = data.get('lesson')

        item_object = course if course else lesson
        item_title = item_object.title

        # Получаем цену из объекта. Умножаем на 100 для Stripe (центы/копейки).
        amount_decimal = item_object.price
        amount_cents = int(amount_decimal * 100)

        if amount_cents <= 0:
            return Response({"error": "Сумма оплаты должна быть больше нуля."}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Создание записи о платеже в БД (до получения ссылки)
        payment = Payment.objects.create(
            user=user,
            course=course,
            lesson=lesson,
            amount=amount_decimal,
            payment_method=Payment.PaymentMethod.TRANSFER,
        )

        # 2. Взаимодействие со Stripe: Продукт -> Цена -> Сессия

        product_stripe = create_stripe_product(item_object)
        if not product_stripe:
            payment.delete()
            return Response({"error": "Не удалось создать продукт Stripe."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        price_stripe = create_stripe_price(product_id=product_stripe.id, amount=amount_cents)
        if not price_stripe:
            payment.delete()
            return Response({"error": "Не удалось создать цену Stripe."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        session_stripe = create_stripe_checkout_session(
            price_id=price_stripe.id,
            payment_object=payment,
            course_or_lesson_title=item_title
        )
        if not session_stripe:
            payment.delete()
            return Response({"error": "Не удалось создать сессию Stripe."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 3. Обновление записи о платеже
        payment.stripe_session_id = session_stripe.id
        payment.payment_link = session_stripe.url
        payment.save()

        return Response({
            "message": "Платеж успешно инициирован. Используйте payment_link для оплаты.",
            "payment_id": payment.pk,
            "payment_link": session_stripe.url,
            "stripe_session_id": session_stripe.id,
        }, status=status.HTTP_201_CREATED)

    # ДОПОЛНИТЕЛЬНОЕ ЗАДАНИЕ
    @action(detail=True, methods=['get'], url_path='check-status',
            description="Проверить статус платежа через Stripe Session Retrieve по ID сессии.")
    def check_status(self, request, pk=None):
        try:
            # Используем get_queryset() для проверки прав доступа
            payment = self.get_queryset().get(pk=pk)
        except Payment.DoesNotExist:
            return Response({"detail": "Платеж не найден."}, status=status.HTTP_404_NOT_FOUND)

        if not payment.stripe_session_id:
            return Response({"detail": "Этот платеж не был инициирован через Stripe или не имеет ID сессии."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Получение сессии из Stripe
        session_stripe = retrieve_stripe_session(payment.stripe_session_id)

        if not session_stripe:
            return Response({"error": "Не удалось получить данные о сессии Stripe."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Обновление локального статуса, если оплата подтверждена
        if session_stripe.payment_status == 'paid' and not payment.is_paid:
            payment.is_paid = True
            payment.save()

        return Response({
            "payment_id": payment.pk,
            "stripe_session_id": payment.stripe_session_id,
            "local_status": "Оплачено" if payment.is_paid else "Не оплачено",
            "stripe_payment_status": session_stripe.payment_status,
            "stripe_url": payment.payment_link
        }, status=status.HTTP_200_OK)