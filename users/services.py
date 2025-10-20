import stripe
from django.conf import settings

# Устанавливаем ключ API Stripe из настроек
stripe.api_key = settings.STRIPE_SECRET_KEY

def create_stripe_product(name: str):
    """
    Создает продукт в Stripe.
    Продукт - это то, что вы продаете (например, "Курс по Python").
    """
    try:
        product = stripe.Product.create(name=name)
        return product
    except Exception as e:
        print(f"Ошибка создания продукта Stripe: {e}")
        return None

def create_stripe_price(product_id: str, amount: int, currency: str = 'rub'):
    """
    Создает цену для продукта в Stripe.
    'amount' должен быть в копейках (int).
    """
    try:
        price = stripe.Price.create(
            product=product_id,
            unit_amount=amount, # Сумма в копейках
            currency=currency,
        )
        return price
    except Exception as e:
        print(f"Ошибка создания цены Stripe: {e}")
        return None

def create_stripe_session(price_id: str):
    """
    Создает сессию Checkout в Stripe для получения ссылки на оплату.
    """
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='payment',
            success_url=settings.STRIPE_SUCCESS_URL, # URL при успехе
            cancel_url=settings.STRIPE_CANCEL_URL,   # URL при отмене
        )
        return session
    except Exception as e:
        print(f"Ошибка создания сессии Stripe: {e}")
        return None

def retrieve_stripe_session(session_id: str):
    """
    (Дополнительное задание)
    Получает информацию о сессии Stripe для проверки статуса оплаты.
    """
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return session
    except Exception as e:
        print(f"Ошибка получения сессии Stripe: {e}")
        return None