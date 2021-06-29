from django.contrib.auth import get_user_model
from django.core.mail import send_mail
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
    event = models.ForeignKey('Event', on_delete=models.CASCADE,
                              related_name='tracks', verbose_name=_('Событие'))
    # https://docs.djangoproject.com/en/dev/topics/db/models/#extra-fields-on-many-to-many-relationships
    # https://docs.djangoproject.com/en/3.2/ref/models/fields/
    participants = models.ManyToManyField(get_user_model(),
                                          related_name='tracks',
                                          verbose_name=_('Участники трэка'),
                                          blank=True,
                                          through='TrackChoice',
                                          through_fields=(
                                          'track', 'participant')
                                          )
    interested = models.ManyToManyField(get_user_model(),
                                        related_name='interested_tracks',
                                        verbose_name=_(
                                            'Заинтересованные сотрудники'),
                                        blank=True)

    class Meta:
        verbose_name = _('Трек')
        verbose_name_plural = _('Треки')

    def __str__(self):
        return f'Трек: {self.title} Событие: {self.event}'


class TrackChoice(models.Model):
    """
    Модель(таблица) для связи статуса участника в определенном треке
    """
    participant = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,
                                    verbose_name=_('Участник'))
    track = models.ForeignKey(Track, on_delete=models.CASCADE,
                              verbose_name=_('Выбранный трек'))
    change_time = models.DateTimeField(auto_now=True, verbose_name=_(
        'Последнее время изменения'))
    task_url = models.URLField(verbose_name=_('Ссылка на тестовое задание'),
                               blank=True)
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
    last_modified = models.DateTimeField(auto_now=True,
                                         verbose_name=_('Последние изменения'))
    score = models.IntegerField(choices=((i, i) for i in range(1, 6)),
                                verbose_name=_('Оценка'))
    reviewer = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,
                                 verbose_name=_('Ревьювер'))
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


@receiver(signals.pre_save, sender=TrackChoice)
def notification(sender, instance, **kwargs):
    if instance.id:
        old_instance = TrackChoice.objects.get(id=instance.id)
        if old_instance.status != instance.status:
            participant_interested_users = set(User.objects.get(
                email=instance.participant
            ).interested.values_list('email', flat=True))
            track_interested_users = set(Track.objects.get(
                id=instance.track.id
            ).interested.values_list('email', flat=True))
            interested_users = participant_interested_users.union(track_interested_users)
            print(interested_users)
            notification_message = f'У участника {instance.participant.email} ' \
                                   f'(трек {instance.track.title}) изменился статус.\n' \
                                   f'Обновленный статус - {instance.status} '

            send_mail(subject="Обновление статуса участника",
                      message=notification_message, from_email=None,
                      recipient_list=interested_users, fail_silently=False)
