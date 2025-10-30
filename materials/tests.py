from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from materials.models import Course, Lesson, Subscription

User = get_user_model()


class MaterialsAPITestCase(APITestCase):
    """
    Базовый класс для тестов API материалов.
    Создает пользователей (обычный, модератор, другой) и учебные материалы.
    """

    def setUp(self):
        # Создание пользователей
        self.user = User.objects.create_user(email='test@user.com', password='testpassword')
        self.other_user = User.objects.create_user(email='other@user.com', password='testpassword')
        self.moderator = User.objects.create_user(email='moderator@test.com', password='testpassword')

        # Создание и назначение группы модераторов
        moderator_group, created = Group.objects.get_or_create(name='moderators')
        self.moderator.groups.add(moderator_group)

        # Создание курса и урока, принадлежащих 'self.user'
        self.course = Course.objects.create(title='Test Course', owner=self.user)
        self.lesson = Lesson.objects.create(
            title='Test Lesson',
            course=self.course,
            owner=self.user,
            video_url='https://www.youtube.com/watch?v=test'
        )

        # Создание курса, принадлежащего 'self.other_user'
        self.other_course = Course.objects.create(title='Other Test Course', owner=self.other_user)


class CourseAPITests(MaterialsAPITestCase):
    """Тесты для эндпоинтов курсов (Course)."""

    def test_list_courses(self):
        """
        Тестирование списка курсов:
        - Обычный пользователь видит только свои курсы.
        - Модератор видит все курсы.
        """
        # Аутентификация как владелец
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse('materials:course-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Пользователь должен видеть только свой курс
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], self.course.title)

        # Аутентификация как модератор
        self.client.force_authenticate(self.moderator)
        response = self.client.get(reverse('materials:course-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Модератор должен видеть все курсы
        self.assertEqual(len(response.data['results']), 2)

    def test_create_course(self):
        """Тестирование создания курса."""
        self.client.force_authenticate(self.user)
        data = {'title': 'New Course', 'description': 'A new course description.'}
        response = self.client.post(reverse('materials:course-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 3)
        # Проверяем, что владелец курса - текущий пользователь
        new_course = Course.objects.get(id=response.data['id'])
        self.assertEqual(new_course.owner, self.user)

    def test_retrieve_course(self):
        """
        Тестирование получения курса:
        - Владелец может просматривать свой курс.
        - Модератор может просматривать любой курс.
        - Другой пользователь не может просматривать чужой курс.
        """
        # Владелец
        self.client.force_authenticate(self.user)
        url = reverse('materials:course-detail', kwargs={'pk': self.course.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Модератор
        self.client.force_authenticate(self.moderator)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Другой пользователь (должен получить 404, т.к. queryset фильтруется)
        self.client.force_authenticate(self.other_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_course(self):
        """
        Тестирование обновления курса:
        - Владелец может обновлять свой курс.
        - Модератор может обновлять любой курс.
        - Другой пользователь не может обновлять чужой курс.
        """
        data = {'title': 'Updated Course Title'}
        url = reverse('materials:course-detail', kwargs={'pk': self.course.pk})

        # Владелец
        self.client.force_authenticate(self.user)
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course.refresh_from_db()
        self.assertEqual(self.course.title, 'Updated Course Title')

        # Модератор
        data_mod = {'title': 'Moderator Updated Title'}
        self.client.force_authenticate(self.moderator)
        response = self.client.patch(url, data_mod, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course.refresh_from_db()
        self.assertEqual(self.course.title, 'Moderator Updated Title')

        # Другой пользователь
        self.client.force_authenticate(self.other_user)
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_course(self):
        """
        Тестирование удаления курса:
        - Владелец может удалить свой курс.
        - Модератор не может удалить курс (только владелец).
        - Другой пользователь не может удалить чужой курс.
        """
        url = reverse('materials:course-detail', kwargs={'pk': self.course.pk})

        # Попытка удаления модератором (должна быть запрещена)
        self.client.force_authenticate(self.moderator)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Попытка удаления другим пользователем (должна быть запрещена)
        self.client.force_authenticate(self.other_user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Удаление владельцем
        self.client.force_authenticate(self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Course.objects.filter(pk=self.course.pk).exists())


class LessonAPITests(MaterialsAPITestCase):
    """Тесты для эндпоинтов уроков (Lesson) и валидатора URL."""

    def test_create_lesson(self):
        """Тестирование создания урока."""
        self.client.force_authenticate(self.user)
        data = {
            'title': 'New Lesson',
            'course': self.course.pk,
            'description': 'Test description',
            'video_url': 'https://www.youtube.com/watch?v=newvideo'
        }
        response = self.client.post(reverse('materials:lesson-list-create'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_lesson = Lesson.objects.get(id=response.data['id'])
        self.assertEqual(new_lesson.owner, self.user)

    def test_create_lesson_youtube_validation(self):
        """Тестирование валидации URL-адреса YouTube при создании урока."""
        self.client.force_authenticate(self.user)
        url = reverse('materials:lesson-list-create')
        base_data = {'title': 'Validation Test Lesson', 'course': self.course.pk}
        base_data['description'] = 'Test desc'  # Добавьте для избежания potential issues

        # Неверный URL (не YouTube)
        data_invalid_host = {**base_data, 'video_url': 'https://vimeo.com/123456'}
        response = self.client.post(url, data_invalid_host, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['video_url'][0], 'Разрешены только ссылки на YouTube.')

        # Некорректный URL
        data_malformed_url = {**base_data, 'video_url': 'not-a-valid-url'}
        response = self.client.post(url, data_malformed_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['video_url'][0], 'Некорректная ссылка.')

        # Правильный URL
        data_valid_url = {**base_data, 'video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'}
        response = self.client.post(url, data_valid_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_delete_lesson(self):
        """
        Тестирование удаления урока:
        - Владелец может удалить свой урок.
        - Модератор не может удалить урок.
        """
        url = reverse('materials:lesson-detail', kwargs={'pk': self.lesson.pk})

        # Попытка удаления модератором
        self.client.force_authenticate(self.moderator)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Удаление владельцем
        self.client.force_authenticate(self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lesson.objects.filter(pk=self.lesson.pk).exists())


class SubscriptionTests(MaterialsAPITestCase):
    """Тесты для эндпоинта подписки."""

    def test_toggle_subscription(self):
        """Тестирование добавления и удаления подписки на курс."""
        self.client.force_authenticate(self.user)
        url = reverse('materials:subscription-toggle')
        data = {'course_id': self.course.id}

        # Добавление подписки
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'подписка добавлена')
        self.assertTrue(Subscription.objects.filter(user=self.user, course=self.course).exists())

        # Удаление подписки (повторный запрос)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'подписка удалена')
        self.assertFalse(Subscription.objects.filter(user=self.user, course=self.course).exists())