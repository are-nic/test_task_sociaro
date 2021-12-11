from rest_framework import permissions, generics
from django.contrib.auth import get_user_model

from .serializers import UserSerializer

User = get_user_model()


class CreateUserView(generics.CreateAPIView):
    """
    Конечная точка для создания пользователя
    """

    model = User
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSerializer
