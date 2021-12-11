from rest_framework import generics, authentication, status, viewsets
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .lastfm import lastfm_get
from .mixins import LikedMixin
from .models import Track, Party, RecommendTrack, PlaylistTrack
from .permissions import PartyOwner
from .serializers import PartySerializer, RecommendTrackSerializer, PlayTrackSerializer
from datetime import datetime


class PartyView(viewsets.ModelViewSet):
    """
    Просмотр, создание, редактирование, удаление Мероприятий.

    Доступы: Создать мероприятия могут любые авторизованные пользователи
            Изменять, удалять мероприятия могут владельцы мероприятий и суперпользователь
    """
    queryset = Party.objects.all()
    serializer_class = PartySerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [PartyOwner]
        return [permission() for permission in permission_classes]

    '''def get_queryset(self):
        """
            Вывести мероприятия, которые еще не закрыты. 
            Дата и время закрытия которых больше даты и времени в момент запроса
        """
        return self.queryset.filter(closed__gt=datetime.now())'''

    def perform_create(self, serializer):
        """
        При создании мероприятия текущий юзер становится его создателем
        """
        serializer.save(user=self.request.user)                            # сохраняем мероприятие


class RecommendTracksView(viewsets.ModelViewSet, LikedMixin):
    """
    Для доступа к рекомендованным трекам через мероприятие
    """
    serializer_class = RecommendTrackSerializer

    def get_queryset(self):
        return RecommendTrack.objects.filter(party=self.kwargs['party_pk']).order_by('likes')


@api_view(['GET', 'POST'])
@authentication_classes([authentication.TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_and_suggest_track(request):
    """
    Найти трек.
    При уточнении трек сохранятеся в БД
    """
    artist = request.query_params.get('artist', None)
    track = request.query_params.get('track', None)

    if artist is not None and track is not None:
        if request.method == 'GET':
            r = lastfm_get({
                'method': 'track.search',
                'track': track,
                'artist': artist
            })
            return Response(r.json(), status=status.HTTP_200_OK)

        elif request.method == 'POST':
            r = lastfm_get({
                'method': 'track.getInfo',
                'track': track,
                'artist': artist
            })
            track_name = r.json()['track']['artist']['name'] + ' - ' + r.json()['track']['name']
            track = Track.objects.create(
                name=track_name,
                lastfm_url=r.json()['track']['url']
            )
            track.save()
            return Response(r.json(), status=status.HTTP_200_OK)
    return Response({"error": "Артист или Трек не заданы"}, status=status.HTTP_400_BAD_REQUEST)

