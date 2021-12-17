from django.db.models import Count
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import authentication, status, viewsets, generics
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .lastfm import lastfm_get
from .mixins import LikedMixin
from .models import Track, Party, RecommendTrack, PlaylistTrack
from .permissions import PartyOwner
from .serializers import PartySerializer, RecommendTrackSerializer, PlayTrackSerializer, TrackSerializer
from datetime import datetime
from django.views.decorators.cache import cache_page


class TrackView(generics.ListAPIView):
    """
    Просмотр добавленных в БД Треков.
    """
    queryset = Track.objects.all()
    serializer_class = TrackSerializer
    permission_classes = [IsAuthenticated]


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
        return RecommendTrack.objects.filter(party=self.kwargs['party_pk'])\
                                     .annotate(count=Count('likes'))\
                                     .order_by('-count')

    def create(self, request, *args, **kwargs):
        # сравниваем время и дату, указанные в поле closed Мероприятия с текущими временем и датой
        party_time = Party.objects.get(id=int(self.kwargs['party_pk'])).closed
        if datetime.now().timestamp() < party_time.timestamp():
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response({"error": "Прием заявок окончен"})

    def perform_create(self, serializer):
        serializer.save(party=Party.objects.get(id=int(self.kwargs['party_pk'])))


class PlayTracksView(viewsets.ModelViewSet):
    """
    Для доступа к трекам в плейлисте через мероприятие
    """
    serializer_class = PlayTrackSerializer

    def get_queryset(self):
        return PlaylistTrack.objects.filter(party=self.kwargs['party_pk'])

    def create(self, request, *args, **kwargs):
        # находим значение максимально допустимого кол-ва треков в плейлисте мероприятия
        # и кол-во уже добавленных треков
        max_qty_tracks = Party.objects.get(id=int(self.kwargs['party_pk'])).max_qty_tracks
        playlist_len = PlaylistTrack.objects.filter(party=int(self.kwargs['party_pk'])).count()
        if playlist_len < max_qty_tracks:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response({"error": "Плейлист заполнен"})

    def perform_create(self, serializer):
        serializer.save(party=Party.objects.get(id=int(self.kwargs['party_pk'])))


# задаем возможность указания параметров запроса в swagger ui
@swagger_auto_schema(method='post', manual_parameters=[
    openapi.Parameter('artist', openapi.IN_QUERY,
                      type=openapi.TYPE_STRING),
    openapi.Parameter('track', openapi.IN_QUERY,
                      type=openapi.TYPE_STRING),
    openapi.Parameter('method', openapi.IN_QUERY,
                      type=openapi.TYPE_STRING),
])
@api_view(['POST'])
@authentication_classes([authentication.TokenAuthentication])
@permission_classes([IsAuthenticated])
@cache_page(60)    # 60 сек тайм-аут кэширования
def get_and_suggest_track(request):
    """
    Найти трек.
    При уточнении трек сохранятеся в БД
    """
    artist = request.query_params.get('artist', None)
    track = request.query_params.get('track', None)
    method = request.query_params.get('method', None)
    print(request.query_params)

    if artist and track and method:
        if request.method == 'POST':
            if method == 'all':
                r = lastfm_get({
                    'method': 'track.search',
                    'track': track,
                    'artist': artist
                })
                return Response(r.json(), status=status.HTTP_200_OK)
            if method == 'one':
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
    return Response({"error": "Артист, Трек или Метод неверно заданы"}, status=status.HTTP_400_BAD_REQUEST)