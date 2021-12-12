from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from .likes import add_like


class LikedMixin:
    @action(detail=True, methods=['POST'])
    def like(self, request, pk=None, party_pk=None):
        """
        Лайкает трек.
        """
        obj = self.get_object()
        add_like(obj, request.user)
        return Response({"message": "Вы отдали голос за Трек"}, status=status.HTTP_200_OK)