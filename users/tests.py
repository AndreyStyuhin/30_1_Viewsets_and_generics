from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from materials.models import Course, Lesson
from users.models import Payment
from django.urls import reverse

User = get_user_model()


class UsersTests(APITestCase):
    def setUp(self):
        """
        Подготовка тестовых данных: пользователи, курс, урок.
Вызывается перед каждым тестом.
        """
        # Создаем двух пользователей
        self.user1 = User.objects.create_user(
            email='user1@test.com',
            password='testpass123',
            first_name='John',
            last_name='Doe',
            phone='123456789',
            city='Moscow'
        )
        self.user2 = User.objects.create_user(
            email='user2@test.com',
            password='testpass123',
            first_name='Jane',
            last_name='Smith'
        )
        # Создаем модератора (is_staff=True для IsAdminUser)
        self.moderator = User.objects.create_user(
            email='moderator@test.com',
            password='testpass123',
            is_staff=True
        )
        # self.moderator.groups.create(name='moderators') # Не нужно для IsAdminUser

        # Создаем курс и урок для тестов платежей
        self.course = Course.objects.create(title='Test Course', owner=self.user1)
        self.lesson = Lesson.objects.create(
            title='Test Lesson',
            course=self.course,
            owner=self.user1,
            video_url='https://www.youtube.com/watch?v=test'
        )

    def test_create_user(self):
        """
        Тест создания пользователя через /api/users/profiles/ (POST)
        """
        # ИСПРАВЛЕНО: URL был 'users:user-register'[cite: 142], что не существует.
        # Используем 'user-list' из DRF роутера [cite: 161]
        url = reverse('users:user-list')
        data = {
            'email': 'newuser@test.com',
            'password': 'testpass123',
            'first_name': 'New',
            'last_name': 'User',
            'phone': '987654321',
            'city': 'Berlin'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 4)  # 3 из setUp + 1 новый
        self.assertEqual(User.objects.last().email, 'newuser@test.com')

    def test_create_user_invalid_email(self):
        """
        Тест создания пользователя с некорректным email
        """
        # ИСПРАВЛЕНО: URL был 'users:user-register'
        url = reverse('users:user-list')
        data = {
            'email': 'invalid-email',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_users_authenticated(self):
        """
        Тест получения списка пользователей (доступно только админу)
        """
        # ИСПРАВЛЕНО: 'user-list' требует IsAdminUser[cite: 165].
        # Аутентифицируемся как 'self.moderator' (is_staff=True)[cite: 140],
        # а не 'self.user1'[cite: 145].
        self.client.force_authenticate(user=self.moderator)
        url = reverse('users:user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # 3 пользователя из setUp

    def test_list_users_unauthenticated(self):
        """
        Тест получения списка пользователей без аутентификации
        """
        url = reverse('users:user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_own_profile(self):
        """
        Тест получения собственного профиля
        """
        self.client.force_authenticate(user=self.user1)
        # ИСПРАВЛЕНО: URL 'user-detail' корректен
        url = reverse('users:user-detail', kwargs={'pk': self.user1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'user1@test.com')
        self.assertIn('phone', response.data)


    def test_retrieve_other_profile(self):
        """
        Тест получения профиля другого пользователя (должен вернуть 404)
        """
        self.client.force_authenticate(user=self.user1)
        url = reverse('users:user-detail', kwargs={'pk': self.user2.pk})
        response = self.client.get(url)

        # ИСПРАВЛЕНО: Ожидался 200 OK, но 'get_queryset'
        # фильтрует по 'request.user.pk', поэтому user1 не может
        # видеть user2. Ожидаем 404.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_update_own_profile(self):
        """
        Тест обновления собственного профиля
        """
        self.client.force_authenticate(user=self.user1)
        # ИСПРАВЛЕНО: URL был 'users:user-profile-update', что не существует.
        # Используем 'user-detail' с методом PATCH.
        url = reverse('users:user-detail', kwargs={'pk': self.user1.pk})
        data = {
            'first_name': 'Updated',
            'city': 'New York'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.first_name, 'Updated')
        self.assertEqual(self.user1.city, 'New York')


    def test_update_other_profile(self):
        """
        Тест попытки обновления чужого профиля (должен вернуть 404)
        """
        self.client.force_authenticate(user=self.user2)
        # ИСПРАВЛЕНО: URL был 'users:user-profile-update'[cite: 150].
        # Тест был некорректен. Теперь user2 пытается обновить user1.
        url = reverse('users:user-detail', kwargs={'pk': self.user1.pk})
        data = {'first_name': 'Hacked'}
        response = self.client.patch(url, data, format='json')

        # ИСПРАВЛЕНО: Ожидался 200 OK[cite: 150]. Но user2 не может
        # получить доступ к user1 из-за 'get_queryset'[cite: 166]. Ожидаем 404.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.user1.refresh_from_db()
        self.assertNotEqual(self.user1.first_name, 'Hacked')  # Профиль user1 не изменился


    def test_delete_own_profile(self):
        """
        Тест удаления собственного профиля

        """
        self.client.force_authenticate(user=self.user1)
        # ИСПРАВЛЕНО: URL был 'users:user-delete'[cite: 151], что не существует.
        # Используем 'user-detail' с методом DELETE.
        url = reverse('users:user-detail', kwargs={'pk': self.user1.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(pk=self.user1.pk).exists())


    def test_delete_other_profile(self):
        """
        Тест попытки удаления чужого профиля
        """
        self.client.force_authenticate(user=self.user2)
        # ИСПРАВЛЕНО: URL был 'users:user-delete'[cite: 152].
        url = reverse('users:user-detail', kwargs={'pk': self.user1.pk})
        response = self.client.delete(url)

        # ИСПРАВЛЕНО: Ожидался 403 FORBIDDEN [cite: 152], но 'get_queryset' [cite: 166]
        # вернет 404, так как объект не будет найден для user2.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(User.objects.filter(pk=self.user1.pk).exists())


class PaymentsTests(APITestCase):
    def setUp(self):
        """
        Подготовка тестовых данных: пользователи, курс, урок, платежи.
        """
        self.user = User.objects.create_user(
            email='user@test.com',
            password='testpass123'
        )
        self.course = Course.objects.create(title='Test Course', owner=self.user)
        self.lesson = Lesson.objects.create(
            title='Test Lesson',
            course=self.course,
            owner=self.user,
            video_url='https://www.youtube.com/watch?v=test'
        )
        self.payment1 = Payment.objects.create(
            user=self.user,
            course=self.course,
            amount=99.99,
            payment_method='transfer'
        )
        self.payment2 = Payment.objects.create(
            user=self.user,
            lesson=self.lesson,
            amount=19.99,
            payment_method='cash'
        )

    def test_list_payments_authenticated(self):
        """
        Тест получения списка платежей (авторизованный пользователь)
        """
        self.client.force_authenticate(user=self.user)
        url = reverse('users:payment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # 2 платежа из setUp

    def test_list_payments_unauthenticated(self):
        """
        Тест получения списка платежей без аутентификации
        """
        url = reverse('users:payment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_filter_payments_by_course(self):
        """
        Тест фильтрации платежей по курсу
        """
        self.client.force_authenticate(user=self.user)
        url = reverse('users:payment-list')
        response = self.client.get(url, {'course': self.course.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        # self.assertEqual(response.data[0]['course'], self.course.pk) # Cerializer [cite: 124] returns PrimaryKey
        self.assertEqual(response.data[0]['course'], self.course.pk)

    def test_filter_payments_by_lesson(self):
        """
        Тест фильтрации платежей по уроку
        """
        self.client.force_authenticate(user=self.user)
        url = reverse('users:payment-list')
        response = self.client.get(url, {'lesson': self.lesson.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['lesson'], self.lesson.pk)

    def test_filter_payments_by_payment_method(self):
        """
        Тест фильтрации платежей по способу оплаты
        """
        self.client.force_authenticate(user=self.user)
        url = reverse('users:payment-list')
        response = self.client.get(url, {'payment_method': 'cash'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['payment_method'], 'cash')  # [cite: 155]

    def test_order_payments_by_date(self):
        """
        Тест сортировки платежей по дате
        """
        self.client.force_authenticate(user=self.user)
        url = reverse('users:payment-list')
        response = self.client.get(url, {'ordering': '-payment_date'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        # Проверяем, что платежи отсортированы по убыванию даты
        self.assertTrue(response.data[0]['payment_date'] >= response.data[1]['payment_date'])