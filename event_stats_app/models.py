from django.db import models

from core.models import User


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
    name = models.CharField(max_length=128, verbose_name='Название события')
    date = models.DateField(verbose_name='Дата начала события')


class Track(models.Model):
    """
    Данная модель представляет поток или трэк конкретного события
    """
    # TODO: rename name to title
    name = models.CharField(max_length=128, verbose_name='Название потока')
    event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='tracks', verbose_name='Событие')
    # https://docs.djangoproject.com/en/dev/topics/db/models/#extra-fields-on-many-to-many-relationships
    # https://docs.djangoproject.com/en/3.2/ref/models/fields/
    participants = models.ManyToManyField(User, related_name='tracks', verbose_name='Участники трэка',
                                          blank=True,
                                          through='TrackUserStatus',
                                          through_fields=('track', 'participant')
                                          )
    interested = models.ManyToManyField(User, related_name='interested_tracks',
                                        verbose_name='Заинтересованные сотрудники', blank=True)


# TODO Сделать отдельно модель отзыва, т.к там много параметров
# TODO: Придумать куда внести ссылки на тестовые задания, отзыв ментора и кто оставил отзыв
class TrackUserStatus(models.Model):
    """
    Модель(таблица) для связи статуса участника в определенном треке
    """
    participant = models.ForeignKey(User, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    change_time = models.DateTimeField(auto_now=True)
    # TODO: заменить на choices
    # TODO: добавить verbose name + plural
    status = models.ForeignKey('ParticipantStatus', on_delete=models.CASCADE)


# TODO: Заменить на django-choices
class ParticipantStatus(models.Model):
    """Модель статуса участника в треке"""
    name = models.CharField(max_length=16, verbose_name='Название статуса')

# TODO: Придумать как инициализировать определенные группы сотрудников
# Либо фикстуры, либо миграции, либо apps.py - есть инициализация приложения
# при apps.py можно сделать migrate при диплое, т.е добавить кастомную логику при каждой играции
# прорверять сущестуют ли какие то группы или пользователи
# либо сделать в utils функцию при вызове ...
# лучший способ - писать кастомную миграцию (можно заполнять чем нужно)
# class MentorGroup(Group):
#     pass

# Group: Mentor Сотрудник Участник
