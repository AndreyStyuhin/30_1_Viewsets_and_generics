from django.urls import path
from rest_framework.routers import DefaultRouter
from materials.views import (
    CourseViewSet,
    LessonListCreateView,
    LessonRetrieveUpdateDestroyView
)

app_name = 'materials'

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='courses')

urlpatterns = [
    path('lessons/', LessonListCreateView.as_view(), name='lesson-list-create'),
    path('lessons/<int:pk>/', LessonRetrieveUpdateDestroyView.as_view(), name='lesson-detail'),
] + router.urls