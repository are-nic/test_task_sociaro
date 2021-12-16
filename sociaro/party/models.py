from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Track(models.Model):
    name = models.CharField(max_length=200, verbose_name='Исполнитель и название трека')
    lastfm_url = models.URLField(verbose_name='Ссылка на LastFM', max_length=300, blank=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Трек'
        verbose_name_plural = 'Треки'
        db_table = 'tracks'

    def __str__(self):
        return self.name


class Party(models.Model):
    """ плейлист/событие """

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь', related_name='playlists')
    name = models.CharField(max_length=100, verbose_name='Название мероприятия')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    closed = models.DateTimeField(verbose_name='Мероприятие продлится до')
    max_qty_tracks = models.PositiveIntegerField(default=1, verbose_name='Макс. кол-во треков')

    class Meta:
        ordering = ('name',)
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'
        db_table = 'parties'

    def __str__(self):
        return self.name


class PlaylistTrack(models.Model):
    """
    Трек в плейлисте мероприятия
    """
    party = models.ForeignKey(Party, verbose_name='Мероприятие', on_delete=models.CASCADE, related_name='play_tracks')
    track = models.ForeignKey(Track, verbose_name='Трек плейлиста', on_delete=models.CASCADE)

    class Meta:
        ordering = ('party',)
        verbose_name = 'Трек плейлиста'
        verbose_name_plural = 'Треки плейлиста'
        db_table = 'play_tracks'

    def __str__(self):
        return '{}, {}'.format(self.party.name, self.track.name)


class Like(models.Model):
    user = models.ForeignKey(User, related_name='likes', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


class RecommendTrack(models.Model):
    """
    предложенные треки
    """
    party = models.ForeignKey(Party, verbose_name='Мероприятие', on_delete=models.CASCADE,
                              related_name='recommend_tracks')
    track = models.ForeignKey(Track, verbose_name='Предложенный трек', on_delete=models.CASCADE)
    likes = GenericRelation(Like)

    @property
    def total_likes(self):
        return self.likes.count()

    class Meta:
        verbose_name = 'Предложенный трек'
        verbose_name_plural = 'Предложенные треки'
        db_table = 'recommend_tracks'

    def __str__(self):
        return '{}, {}'.format(self.party.name, self.track.name)