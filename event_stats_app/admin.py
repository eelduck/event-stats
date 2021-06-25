from django.contrib import admin

from core.utils import ExportCsvMixin
from event_stats_app.models import Event, Track, TrackChoice, Feedback


# TODO: Спросить: Стоит ли создавать отдельный раздел под участников через прокси модель?

@admin.register(Event)
class EventAdmin(admin.ModelAdmin, ExportCsvMixin):
    # TODO: Добавить иную фильтрацию по дате
    list_display = ('title', 'date')
    list_filter = ('date',)
    search_fields = ('title', 'date')
    ordering = ('date',)

    actions = ['export_as_csv']


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ('title', 'event')
    list_filter = ('title', 'event')
    search_fields = ('title',)


@admin.register(TrackChoice)
class TrackChoiceAdmin(admin.ModelAdmin):
    list_display = ('participant', 'track', 'status')
    list_filter = ('status', 'track__title', 'track__event')
    search_fields = ('participant__email', 'track__title')


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
