from django.urls import path, include
from rest_framework.routers import DefaultRouter
from materials.views import (
    CourseViewSet,
    LessonListCreateView,
    LessonRetrieveUpdateDestroyView,
    SubscriptionToggleView
)

app_name = 'materials'

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')

urlpatterns = [
    path('lessons/', LessonListCreateView.as_view(), name='lesson-list-create'),
    path('lessons/<int:pk>/', LessonRetrieveUpdateDestroyView.as_view(), name='lesson-detail'),
    path('subscriptions/', SubscriptionToggleView.as_view(), name='subscription-toggle'),
]

urlpatterns += router.urls
