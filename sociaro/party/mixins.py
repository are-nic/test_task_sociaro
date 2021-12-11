from rest_framework.decorators import action
from rest_framework.response import Response

from .likes import add_like


class LikedMixin:
    @action(detail=True, methods=['POST'])
    def like(self, request, pk=None):
        """
        Лайкает `obj`.
        """
        instance = self.get_object()
        add_like(instance, request.user)
        return Response()