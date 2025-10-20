# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Payment

# Если вы используете кастомную модель User
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'payment_date', 'amount', 'course', 'lesson', 'payment_method', 'is_paid')
    list_filter = ('payment_method', 'is_paid')
    search_fields = ('user__email', 'course__title', 'lesson__title')
    readonly_fields = ('stripe_session_id', 'payment_link')