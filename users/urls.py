from django.urls import path
from users.views import (
    UserCreateView,
    UserListView,
    UserRetrieveView,
    UserProfileUpdateView,
    UserDestroyView
)

app_name = 'users'

urlpatterns = [
    path('register/', UserCreateView.as_view(), name='user-register'),
    path('', UserListView.as_view(), name='user-list'),
    path('<int:pk>/', UserRetrieveView.as_view(), name='user-detail'),
    path('<int:pk>/profile/', UserProfileUpdateView.as_view(), name='user-profile-update'),
    path('<int:pk>/delete/', UserDestroyView.as_view(), name='user-delete'),
]