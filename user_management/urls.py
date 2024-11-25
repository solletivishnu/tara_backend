from django.urls import path
from . import views
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/', views.user_registration, name='user_registration'),
    path('activate/<uid>/<token>/', ActivateUserView.as_view(), name='activate'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('protected/', TestProtectedAPIView.as_view(), name='test_protected'),
    # Forgot password view
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),

    # Reset password view
    path('reset-password/<uid>/<token>/', ResetPasswordView.as_view(), name='reset-password'),

    # Refresh token view
    path('refresh-token/', RefreshTokenView.as_view(), name='refresh-token'),

    path('user-details/', UserDetailsListView.as_view(), name='user-details-list'),

    # URL for retrieving, updating, and deleting specific user details
    path('user-details/<int:pk>/', UserDetailsDetailView.as_view(), name='user-details-detail'),

    # firm urls
    path('firmkyc/', FirmKYCView.as_view(), name='firmkyc'),
]
