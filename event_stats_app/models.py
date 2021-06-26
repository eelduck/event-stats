from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import User
from django.db.models import signals
from django.dispatch import receiver
from django.contrib.auth.models import Group


class ParticipantStatus(models.TextChoices):
    REGISTERED = _('Зарегистрировался')
    ON_REVIEW = _('На проверке')
    ACCEPTED = _('Принят')
    DENIED = _('Не принят')
    # HIRED = _('Устроился')


# from django.contrib.auth import get_user_model
# Использовать вместо User
# Это дает быструю замену на твоих пользователей
# TODO: Использовать get_user_model

# TODO: Возможно стоит создать отдельно участника как прокси модель

class Event(models.Model):
    """
    Данная модель хранит события (практикумы)
    """
    title = models.CharField(max_length=128, verbose_name='Название события')
    date = models.DateField(verbose_name='Дата начала события')

    class Meta:
        verbose_name = _('Событие')
        verbose_name_plural = _('События')

    def __str__(self):
        return f'{self.title} {self.date}'


class Track(models.Model):
    """
    Данная модель представляет поток или трэк конкретного события
    """
    title = models.CharField(max_length=128, verbose_name=_('Название потока'))
    event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='tracks', verbose_name=_('Событие'))
    # https://docs.djangoproject.com/en/dev/topics/db/models/#extra-fields-on-many-to-many-relationships
    # https://docs.djangoproject.com/en/3.2/ref/models/fields/
    participants = models.ManyToManyField(get_user_model(), related_name='tracks',
                                          verbose_name=_('Участники трэка'),
                                          blank=True,
                                          through='TrackChoice',
                                          through_fields=('track', 'participant')
                                          )
    interested = models.ManyToManyField(get_user_model(), related_name='interested_tracks',
                                        verbose_name=_('Заинтересованные сотрудники'), blank=True)

    class Meta:
        verbose_name = _('Трек')
        verbose_name_plural = _('Треки')

    def __str__(self):
        return f'Трек: {self.title} Событие: {self.event}'


class TrackChoice(models.Model):
    """
    Модель(таблица) для связи статуса участника в определенном треке
    """
    participant = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name=_('Участник'))
    track = models.ForeignKey(Track, on_delete=models.CASCADE, verbose_name=_('Выбранный трек'))
    change_time = models.DateTimeField(auto_now=True, verbose_name=_('Последнее время изменения'))
    status = models.CharField(
        max_length=32,
        choices=ParticipantStatus.choices,
        default=ParticipantStatus.REGISTERED,
        verbose_name=_('Статус участника'),
    )

    class Meta:
        verbose_name = _('Выбор трека')
        verbose_name_plural = _('Выбор треков')

    def __str__(self):
        return f'{self.participant} {self.track}'


class Feedback(models.Model):
    comment = models.TextField(blank=True, verbose_name=_('Отзыв'))
    last_modified = models.DateTimeField(auto_now=True, verbose_name=_('Последние изменения'))
    score = models.IntegerField(choices=((i, i) for i in range(1, 6)), verbose_name=_('Оценка'))
    reviewer = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name=_('Ревьювер'))
    participant_track_choice = models.ForeignKey(
        TrackChoice,
        on_delete=models.CASCADE,
        related_name='feedback',
        blank=True,
        verbose_name=_('Выбор трека участником'),
    )

    class Meta:
        verbose_name = _('Отзыв')
        verbose_name_plural = _('Отзывы')

    def __str__(self):
        return f'{self.reviewer}'


# signals
@receiver(signals.post_save, sender=TrackChoice)
def notification(sender, instance, created, **kwargs):
    print("email участника: ", instance.participant.email)
    print("трек: ", instance.track.title)
    print("новый статус: ", instance.status)
