from django.contrib import admin

from event_stats_app.models import Participant, ParticipantStatus, Event, Track, TrackUserStatus


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    pass


@admin.register(ParticipantStatus)
class ParticipantStatus(admin.ModelAdmin):
    pass


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    pass


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    pass


@admin.register(TrackUserStatus)
class TrackUserStatusAdmin(admin.ModelAdmin):
    pass
