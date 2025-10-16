from rest_framework.test import APITestCase
from rest_framework import status  # Добавляем импорт
from django.contrib.auth import get_user_model
from django.urls import reverse
from materials.models import Course, Lesson, Subscription

User = get_user_model()

class SubscriptionTests(APITestCase):
    def setUp(self):
        # Создаем пользователя
        self.user = User.objects.create_user(
            email='test@user.com',
            password='testpass123'
        )
        # Создаем курс
        self.course = Course.objects.create(
            title='Test Course',
            owner=self.user
        )

    def test_toggle_subscription(self):
        self.client.force_authenticate(self.user)
        url = reverse('materials:subscription-toggle')
        data = {'course_id': self.course.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'подписка добавлена')
        # Проверяем, что подписка создана
        self.assertTrue(Subscription.objects.filter(user=self.user, course=self.course).exists())
        # Повторный запрос для удаления подписки
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'подписка удалена')
        self.assertFalse(Subscription.objects.filter(user=self.user, course=self.course).exists())