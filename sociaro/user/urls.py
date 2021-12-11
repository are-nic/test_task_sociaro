from django.urls import path
from rest_framework.routers import SimpleRouter
from .views import CreateUserView
from rest_framework.authtoken.views import obtain_auth_token

router = SimpleRouter(trailing_slash=False)

# router.register('current-user', CurrentUserView)

urlpatterns = [
    path('register', CreateUserView.as_view()),     # регистрация
    path('login', obtain_auth_token),               # авторизация/получение токена
]
urlpatterns += router.urls