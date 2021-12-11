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
    track = serializers.SlugRelatedField(slug_field='name', queryset=Track.objects.all())
    is_like = serializers.SerializerMethodField()

    class Meta:
        model = RecommendTrack
        fields = ['id', 'track', 'is_like', 'total_likes']

    def get_is_like(self, obj):
        """
            Проверяет, лайкнул ли текущий юзер данный трек (`obj`).
        """
        user = self.context.get('request').user
        return is_like(obj, user)


class PlayTrackSerializer(serializers.ModelSerializer):
    """
    Рекомендованные треки
    """
    track = serializers.SlugRelatedField(slug_field='name', queryset=Track.objects.all())

    class Meta:
        model = PlaylistTrack
        # fields = '__all__'
        exclude = ['party']


class PartySerializer(serializers.ModelSerializer):
    """
    Плейлист мероприятия
    """
    user = serializers.ReadOnlyField(source='user.username')
    play_tracks = PlayTrackSerializer(many=True)
    recommend_tracks = RecommendTrackSerializer(many=True)

    class Meta:
        model = Party
        fields = '__all__'
