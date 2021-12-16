from django.urls import path
from .views import CreateUserView
from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
    path('register', CreateUserView.as_view()),     # регистрация
    path('login', obtain_auth_token),               # авторизация/получение токена
]