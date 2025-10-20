from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class UserManager(BaseUserManager):
    """
    Кастомный менеджер для модели User,
    где email используется для аутентификации вместо username.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Создает и сохраняет пользователя с email и паролем.
        """
        if not email:
            raise ValueError(_('Email должен быть указан'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Создает и сохраняет суперпользователя с email и паролем.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)



class User(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    phone = models.CharField(max_length=35, blank=True, null=True, verbose_name='Телефон')
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name='Город')
    avatar = models.ImageField(upload_to='users/avatars/', blank=True, null=True, verbose_name='Аватар')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Наличные'),
        ('transfer', 'Перевод (Stripe)'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments',
                             verbose_name='Пользователь')
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата оплаты')

    course = models.ForeignKey('materials.Course', on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='payments', verbose_name='Оплаченный курс')
    lesson = models.ForeignKey('materials.Lesson', on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='payments', verbose_name='Оплаченный урок')

    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма оплаты')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, verbose_name='Способ оплаты')

    is_paid = models.BooleanField(default=False, verbose_name='Статус оплаты')
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True, verbose_name='ID сессии Stripe')
    payment_link = models.URLField(max_length=500, blank=True, null=True, verbose_name='Ссылка на оплату')

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
        ordering = ('-payment_date',)

    def __str__(self):
        return f'Платеж от {self.user} на сумму {self.amount} (Paid: {self.is_paid})'