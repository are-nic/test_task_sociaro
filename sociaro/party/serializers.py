from rest_framework import serializers

from .likes import is_like
from .models import Party, Track, RecommendTrack, PlaylistTrack


class TrackSerializer(serializers.ModelSerializer):
    """
    Треки, хранящиеся в БД
    """
    class Meta:
        model = Track
        fields = '__all__'


class RecommendTrackSerializer(serializers.ModelSerializer):
    """
    Рекомендованные треки
    """
    party = serializers.ReadOnlyField(source='party.name')
    track = serializers.SlugRelatedField(slug_field='name', queryset=Track.objects.all())
    is_like = serializers.SerializerMethodField()

    class Meta:
        model = RecommendTrack
        fields = ['id', 'party', 'track', 'is_like', 'total_likes']

    def get_is_like(self, obj):
        """
            Проверяет, отдали ли голос текущий юзер за данный трек (`obj`).
        """
        user = self.context.get('request').user
        return is_like(obj, user)


class PlayTrackSerializer(serializers.ModelSerializer):
    """
    Треки плейлиста
    """
    party = serializers.ReadOnlyField(source='party.name')
    track = serializers.SlugRelatedField(slug_field='name', queryset=Track.objects.all())

    class Meta:
        model = PlaylistTrack
        fields = '__all__'


class PartySerializer(serializers.ModelSerializer):
    """
    Плейлист мероприятия
    """
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Party
        fields = '__all__'
