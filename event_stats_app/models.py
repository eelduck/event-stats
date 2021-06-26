from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import User
from django.db.models import signals
from django.dispatch import receiver

# TODO: Спросить про преимущества django-choices (если таковые есть)
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

# TODO: Добавить всем Fields verbose_name

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
    title = models.CharField(max_length=128, verbose_name='Название потока')
    event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='tracks', verbose_name='Событие')
    # https://docs.djangoproject.com/en/dev/topics/db/models/#extra-fields-on-many-to-many-relationships
    # https://docs.djangoproject.com/en/3.2/ref/models/fields/
    participants = models.ManyToManyField(User, related_name='tracks', verbose_name='Участники трэка',
                                          blank=True,
                                          through='TrackChoice',
                                          through_fields=('track', 'participant')
                                          )
    interested = models.ManyToManyField(User, related_name='interested_tracks',
                                        verbose_name='Заинтересованные сотрудники', blank=True)

    class Meta:
        verbose_name = _('Трек')
        verbose_name_plural = _('Треки')

    def __str__(self):
        return f'Трек: {self.title} Событие: {self.event}'


class TrackChoice(models.Model):
    """
    Модель(таблица) для связи статуса участника в определенном треке
    """
    participant = models.ForeignKey(User, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    change_time = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=32,
        choices=ParticipantStatus.choices,
        default=ParticipantStatus.REGISTERED,
    )

    class Meta:
        verbose_name = _('Выбор трека')
        verbose_name_plural = _('Выбор треков')

    def __str__(self):
        return f'{self.participant} {self.track}'


class Feedback(models.Model):
    comment = models.TextField(blank=True)
    last_modified = models.DateTimeField(auto_now=True)
    score = models.IntegerField(choices=((i, i) for i in range(1, 6)), verbose_name=_('Оценка'))
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    participant_track_choice = models.ForeignKey(
        TrackChoice,
        on_delete=models.CASCADE,
        related_name='feedback',
        blank=True
    )

    class Meta:
        verbose_name = _('Отзыв')
        verbose_name_plural = _('Отзывы')

    def __str__(self):
        return f'{self.reviewer}'

# TODO: Придумать как инициализировать определенные группы сотрудников
# Либо фикстуры, либо миграции, либо apps.py - есть инициализация приложения
# при apps.py можно сделать migrate при диплое, т.е добавить кастомную логику при каждой играции
# прорверять сущестуют ли какие то группы или пользователи
# либо сделать в utils функцию при вызове ...
# лучший способ - писать кастомную миграцию (можно заполнять чем нужно)
# class MentorGroup(Group):
#     pass

# Group: Mentor Сотрудник Участник

class Group(models.Model):
    title = models.TextField(max_length=128, verbose_name='Название группы')
    description = models.TextField(max_length=255, verbose_name='Описание группы')

class MentorGroup(models.Model):
    """
    Модель(таблица) для связи ментор - группа(группы)
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    change_time = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Группа')
        verbose_name_plural = _('Группы')



# signals

@receiver(signals.post_save, sender=TrackChoice)
def notification(sender, instance, created, **kwargs):
    print ("email участника: ", instance.participant.email)
    print ("трек: ", instance.track.title)
    print ("новый статус: ", instance.status)
