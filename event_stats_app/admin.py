from django.contrib import admin

from core.utils import ExportCsvMixin
from event_stats_app.models import Event, Track, TrackChoice, Feedback


# TODO: Спросить: Стоит ли создавать отдельный раздел под участников через прокси модель?

@admin.register(Event)
class EventAdmin(admin.ModelAdmin, ExportCsvMixin):
    actions = ['export_as_csv']


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    pass


@admin.register(TrackChoice)
class TrackChoiceAdmin(admin.ModelAdmin):
    pass


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    pass
