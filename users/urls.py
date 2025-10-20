from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet

router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payment')

app_name = 'users'

urlpatterns = [
#    path('register/', UserCreateView.as_view(), name='user-register'),
#    path('', UserListView.as_view(), name='user-list'),
#    path('<int:pk>/', UserRetrieveView.as_view(), name='user-detail'),
#    path('profile/', UserProfileUpdateView.as_view(), name='user-profile-update'),
#    path('<int:pk>/delete/', UserDestroyView.as_view(), name='user-delete'),
#    path('payments/', PaymentListView.as_view(), name='payment-list'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
]