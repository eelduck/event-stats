from django.contrib import admin, messages
from django.db.models import Count, QuerySet
from django.urls import path
from django.utils.translation import gettext_lazy as _

from core.models import CustomUser
from core.utils import ExportCsvMixin
from event_stats_app.models import Event, Track, TrackChoice, Feedback, ParticipantStatus
# TODO: Спросить: Стоит ли создавать отдельный раздел под участников через прокси модель?
from event_stats_app.views import AttachUrlWizard


@admin.register(Event)
class EventAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = (
        'title',
        'date',
        'participants_count',
        'applications_count',
        'attached_task_count',
        'accepted_count',
    )
    list_filter = ('date',)
    search_fields = ('title', 'date')
    ordering = ('date',)

    actions = ['export_as_csv']

    def get_queryset(self, request):
        queryset: QuerySet = super().get_queryset(request)
        queryset: QuerySet = queryset.annotate(
            # distinct=True - количество уникальных сущностей
            _participants_count=Count('tracks__participants', distinct=True),
            _applications_count=Count('tracks__participants'),

        )
        return queryset

    @admin.display(ordering='_participants_count', description=_('Участники'))
    def participants_count(self, obj):
        return obj._participants_count

    @admin.display(ordering='_applications_count', description=_('Заявки'))
    def applications_count(self, obj):
        """
        Количество заявок на все треки, может быть больше чем количество пользователей
        """
        return obj._applications_count

    @admin.display(description=_('Количество ТЗ'))
    def attached_task_count(self, obj) -> int:
        """
        Количество сданных тестовых заданий (ТЗ)
        Считается по наличию ссылки на ТЗ, через поиск по трэку
        и эксфильтрацию пустых и Null значений
        """
        count = 0
        for track in obj.tracks.all():
            tc = TrackChoice.objects.filter(track_id=track.id)
            count += tc.exclude(task_url__isnull=True) \
                .exclude(task_url__exact='') \
                .count()
        return count

    @admin.display(description=_('Принято'))
    def accepted_count(self, obj) -> int:
        """
        Количество участников со статусом ACCEPTED
        """
        count = 0
        for track in obj.tracks.all():
            tc = TrackChoice.objects.filter(track_id=track.id)
            count += tc.filter(status=ParticipantStatus.ACCEPTED).count()
        return count


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'event',
        'participants_count',
        'attached_task_count',
        'accepted_count'
    )
    list_filter = ('title', 'event')
    search_fields = ('title',)
    filter_horizontal = ('interested',)

    actions = ['subscribe_to_track']

    def get_queryset(self, request):
        queryset: QuerySet = super().get_queryset(request)
        queryset: QuerySet = queryset.annotate(
            _participants_count=Count('participants', distinct=True),
        )
        return queryset

    @admin.display(ordering='_participants_count', description=_('Участники'))
    def participants_count(self, obj) -> int:
        """
        Подсчет количество участников (заявок) в треке
        """
        return obj._participants_count

    def _filter_track_choices_by(self, obj, status) -> QuerySet:
        """
        Фильтрация выбора треков (участников трека) по статусу
        """
        return TrackChoice.objects.filter(track_id=obj.id, status=status)

    @admin.display(description=_('Принято'))
    def accepted_count(self, obj) -> int:
        """
        Количество участников со статусом ACCEPTED
        """
        accepted: QuerySet = self._filter_track_choices_by(obj, ParticipantStatus.ACCEPTED)
        return accepted.count()

    @admin.display(description=_('Количество ТЗ'))
    def attached_task_count(self, obj) -> int:
        """
        Количество сданных тестовых заданий (ТЗ)
        Считается по наличию ссылки на ТЗ, через поиск по трэку
        и эксфильтрацию пустых и Null значений
        """
        return TrackChoice.objects \
            .filter(track_id=obj.id) \
            .exclude(task_url__isnull=True) \
            .exclude(task_url__exact='') \
            .count()

    @admin.action(description='Подписаться')
    def subscribe_to_track(self, request, queryset):
        for track in queryset:
            track.interested.add(
                CustomUser.objects.get(email=request.user.email))
        messages.add_message(request, messages.SUCCESS,
                             f'Подписка на треки прошла успешно')


# TODO: Добавить кастомную фильтрацию по дате
@admin.register(TrackChoice)
class TrackChoiceAdmin(admin.ModelAdmin):
    list_display = ('participant', 'track', 'status')
    list_filter = ('status', 'track__title', 'track__event', 'track__event__date')
    search_fields = ('participant__email', 'track__title')

    actions = ['add_link_to_task', 'export_as_csv']

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('add-link-to-task/', AttachUrlWizard.as_view(), name='task_link'),
        ]
        return my_urls + urls

    @admin.action(description='Прикрепить ссылку на ТЗ')
    def add_link_to_task(self, request):
        """
        Добавление ссылки на тестовое и изменение статуса на ON_REVIEW
        Заглушка для вывода экшена
        """
        pass

    add_link_to_task.action_type = 1
    add_link_to_task.action_url = 'add-link-to-task'
    add_link_to_task.confirm = False


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('reviewer', 'participant_track_choice', 'score', 'comment')
    # TODO: Уменьшить количество почт
    list_filter = (
        'score',
        'participant_track_choice__track__title',
        'participant_track_choice__track__event__title',
        'reviewer__email',
    )
    search_fields = ('score', 'reviewer__email')
    raw_id_fields = ('participant_track_choice',)
