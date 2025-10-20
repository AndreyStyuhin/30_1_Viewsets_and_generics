# users/services.py
import stripe
from django.conf import settings
from materials.models import Course, Lesson

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_stripe_product(item_object):
    """Создает продукт в Stripe для курса или урока."""
    if isinstance(item_object, Course):
        name = f"Курс: {item_object.title}"
        description = item_object.description
    elif isinstance(item_object, Lesson):
        name = f"Урок: {item_object.title} ({item_object.course.title})"
        description = item_object.description
    else:
        raise ValueError("Неподдерживаемый тип объекта для Stripe Product.")

    try:
        product = stripe.Product.create(
            name=name,
            description=description,
            type='service',
        )
        return product
    except stripe.error.StripeError as e:
        print(f"Ошибка при создании продукта Stripe: {e}")
        return None

def create_stripe_price(product_id: str, amount: int, currency: str = 'rub'):
    """Создает цену в Stripe (amount в копейках/центах)."""
    # Важно: Stripe ожидает сумму в наименьших единицах валюты (например, копейки для рублей, центы для USD)
    try:
        price = stripe.Price.create(
            currency=currency,
            unit_amount=amount,
            product=product_id,
        )
        return price
    except stripe.error.StripeError as e:
        print(f"Ошибка при создании цены Stripe: {e}")
        return None

def create_stripe_checkout_session(price_id: str, payment_object, course_or_lesson_title: str):
    """Создает сессию Stripe Checkout и возвращает объект сессии."""
    try:
        session = stripe.checkout.Session.create(
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='payment',
            success_url=settings.STRIPE_SUCCESS_URL + f"?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=settings.STRIPE_CANCEL_URL,
            metadata={
                'payment_id': payment_object.pk,
                'user_email': payment_object.user.email,
                'item_title': course_or_lesson_title,
            }
        )
        return session
    except stripe.error.StripeError as e:
        print(f"Ошибка при создании сессии Stripe: {e}")
        return None

def retrieve_stripe_session(session_id: str):
    """Получает данные о сессии по идентификатору (Дополнительное задание)."""
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return session
    except stripe.error.StripeError as e:
        print(f"Ошибка при получении сессии Stripe: {e}")
        return None