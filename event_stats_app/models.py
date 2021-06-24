from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import User


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
# Когда создаешь собственную модель не нужно линковаться с ???
# get_user_model
# TODO: Спросить про момент из книги


class Event(models.Model):
    """
    Данная модель хранит события (практикумы)
    """
    title = models.CharField(max_length=128, verbose_name='Название события')
    date = models.DateField(verbose_name='Дата начала события')


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


# TODO Сделать отдельно модель отзыва, т.к там много параметров
# TODO: Придумать куда внести ссылки на тестовые задания, отзыв ментора и кто оставил отзыв
class TrackChoice(models.Model):
    """
    Модель(таблица) для связи статуса участника в определенном треке
    """
    participant = models.ForeignKey(User, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    change_time = models.DateTimeField(auto_now=True)
    # TODO: заменить на choices
    # TODO: добавить verbose name + plural
    status = models.CharField(
        max_length=32,
        choices=ParticipantStatus.choices,
        default=ParticipantStatus.REGISTERED,
    )


class Feedback(models.Model):
    comment = models.TextField(blank=True)
    last_modified = models.DateTimeField(auto_now=True)
    score = models.IntegerField(choices=((i, i) for i in range(1, 6)))
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    participant_track_choice = models.ForeignKey(TrackChoice, on_delete=models.CASCADE, related_name='feedback',
                                                 blank=True)

# TODO: Придумать как инициализировать определенные группы сотрудников
# Либо фикстуры, либо миграции, либо apps.py - есть инициализация приложения
# при apps.py можно сделать migrate при диплое, т.е добавить кастомную логику при каждой играции
# прорверять сущестуют ли какие то группы или пользователи
# либо сделать в utils функцию при вызове ...
# лучший способ - писать кастомную миграцию (можно заполнять чем нужно)
# class MentorGroup(Group):
#     pass

# Group: Mentor Сотрудник Участник
