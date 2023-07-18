from django.urls import path, include
from accounts.views import (
    GoogleCallbackAPIView, GoogleToDjangoLoginView
    )

urlpatterns = [
    path('google/token/', GoogleCallbackAPIView.as_view()),
    path('google/login/success/', GoogleToDjangoLoginView.as_view()),
]