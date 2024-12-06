from django.urls import path
from . import views
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/', views.user_registration, name='user_registration'),
    path('users-creation/', views.users_creation, name='user-create'),
    path('activate/<uid>/<token>/', ActivateUserView.as_view(), name='activate'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('protected/', TestProtectedAPIView.as_view(), name='test_protected'),
    # Forgot password view
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),

    # Reset password view
    path('reset-password/<uid>/<token>/', ResetPasswordView.as_view(), name='reset-password'),

    # Refresh token view
    path('refresh-token/', RefreshTokenView.as_view(), name='refresh-token'),

    path('users-kyc/', UsersKYCListView.as_view(), name='user-kyc-list'),

    # URL for retrieving, updating, and deleting specific user details
    path('users-kyc/<int:pk>/', UsersKYCDetailView.as_view(), name='user-kyc-detail'),

    # firm urls
    path('firmkyc/', FirmKYCView.as_view(), name='firmkyc'),

    path('update-users-info', views.partial_update_user, name='partial_update_user'),

    path('services/', ServicesMasterDataAPIView.as_view()),  # For GET (list) and POST

    path('services/<int:pk>/', ServicesMasterDataAPIView.as_view()),  # For GET (detail), PUT, DELETE

    # URL for retrieving a list of visa applications or details of a specific visa application
    path('visa-applications/', VisaApplicationsAPIView.as_view(), name='visa-application-list'),

    # URL for retrieving a specific visa application by its ID
    path('visa-applications/<int:pk>/', VisaApplicationsAPIView.as_view(), name='visa-application-detail'),

    # URL for bulk creating visa applications (POST method)
    path('visa-applications/bulk/', VisaApplicationsAPIView.as_view(), name='visa-application-bulk-create'),

    # URL for updating an existing visa application by ID (PUT method)
    path('visa-applications/<int:pk>/update/', VisaApplicationsAPIView.as_view(), name='visa-application-update'),

    # URL for deleting a visa application by ID (DELETE method)
    path('visa-applications/<int:pk>/delete/', VisaApplicationsAPIView.as_view(), name='visa-application-delete'),

]
