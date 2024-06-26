from django.urls import path, include
from accounts.views import (
    GoogleCallbackAPIView, UserInfoView
    )
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('/google/token', GoogleCallbackAPIView.as_view(), name='google_callback'),
    path('/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('', UserInfoView.as_view(), name='user_info')
]