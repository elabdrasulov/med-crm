from django.urls import path

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import *

urlpatterns = [
    path('register/', RegisterAPIView.as_view()),
    path('activate/<str:activation_code>/', activate),
    path('change_password/', ChangePasswordView.as_view()),
    path('forgot_password/', ForgotPasswordView.as_view()),
    path('password_confirm/<str:activation_code>/', NewPasswordView.as_view()),
    path('login/', TokenObtainPairView.as_view()),
    path('logout/', LogoutAPIView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view()),
]
