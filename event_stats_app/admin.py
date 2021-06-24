from django.contrib import admin

from event_stats_app.models import Event, Track, TrackChoice


# TODO: Спросить: Стоит ли создавать отдельный раздел под участников через прокси модель?

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    pass


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    pass


@admin.register(TrackChoice)
class TrackUserStatusAdmin(admin.ModelAdmin):
    pass
