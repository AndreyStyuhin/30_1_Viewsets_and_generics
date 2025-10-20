from django.urls import path
from rest_framework.routers import DefaultRouter
from materials.apps import MaterialsConfig
from materials.views import CourseViewSet, LessonListCreateAPIView, LessonRetrieveUpdateDestroyAPIView, SubscriptionAPIView

app_name = MaterialsConfig.name

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')

urlpatterns = [
    # Эндпоинты для уроков (согласно тестам)
    path('lessons/', LessonListCreateAPIView.as_view(), name='lesson-list-create'),
    path('lessons/<int:pk>/', LessonRetrieveUpdateDestroyAPIView.as_view(), name='lesson-detail'),

    # Эндпоинт для подписки
    path('subscriptions/', SubscriptionAPIView.as_view(), name='subscription-toggle'),

] + router.urls