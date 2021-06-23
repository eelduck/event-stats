from django.db import models
from django.contrib.auth.models import User, Group


class Participant(models.Model):
    first_name = models.CharField(max_length=64, verbose_name='Имя')
    middle_name = models.CharField(max_length=64, verbose_name='Отчество', null=True)
    last_name = models.CharField(max_length=64, verbose_name='Фамилия')
    email = models.EmailField()
    # TODO: Придумать что делать при выборе нескольких направлений
    # phone_number = models.Field
    # status = models.OneToOneField()
    interested = models.ManyToManyField(User, related_name='interested_participants',
                                        verbose_name='Заинтересованные сотрудники', blank=True)


class Event(models.Model):
    """
    Данная модель хранит события (практикумы)
    """
    name = models.CharField(max_length=128, verbose_name='Название события')
    date = models.DateField(verbose_name='Дата начала события')


class Track(models.Model):
    """
    Данная модель представляет поток или трэк конкретного события
    """
    name = models.CharField(max_length=128, verbose_name='Название потока')
    event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='tracks', verbose_name='Событие')
    # https://docs.djangoproject.com/en/dev/topics/db/models/#extra-fields-on-many-to-many-relationships
    # https://docs.djangoproject.com/en/3.2/ref/models/fields/
    participants = models.ManyToManyField('Participant', related_name='tracks', verbose_name='Участники трэка',
                                          blank=True,
                                          through='TrackUserStatus',
                                          through_fields=('track', 'participant')
                                          )
    interested = models.ManyToManyField(User, related_name='interested_tracks',
                                        verbose_name='Заинтересованные сотрудники', blank=True)


class TrackUserStatus(models.Model):
    """
    Модель(таблица) для связи статуса участника в определенном треке
    """
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    change_time = models.DateTimeField(auto_now=True)
    status = models.ForeignKey('ParticipantStatus', on_delete=models.CASCADE)


class ParticipantStatus(models.Model):
    name = models.CharField(max_length=16, verbose_name='Название статуса')


class MentorGroup(Group):
    pass
