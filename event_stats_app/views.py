from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404, render

from core.admin import ExcelImportForm
from core.utils import ExcelImportService
from .models import User, TrackChoice, ParticipantStatus
from .models import Event


def index(request):
    return redirect('/admin')


# statistic
def stat(request):
    users: set = {tc.participant for tc in TrackChoice.objects.all()}
    events = Event.objects.all()

    for event in events:
        # Количество зарегистрированных заявок
        registered_counts = []
        # Количество принятых заявок
        accepted_counts = []
        for track in event.tracks.all():
            track_choices = TrackChoice.objects.filter(track_id=track.id)
            # Участники трека == Зарегистрированные участники
            # (т.е все, кто есть, все они зарегистрированы)
            track_participants = [x.participant for x in track_choices]
            registered_count = len(track_participants)
            # TODO: Смерджить, чтобы получить поле task_url
            # Участники, приложившие тестовое задание
            # attached_task = [x.participant for x in track_choices if x.task_url]
            accepted_participants = [x.participant for x in track_choices if
                                     x.participant == ParticipantStatus.ACCEPTED]
            accepted_count = len(accepted_participants)
            registered_counts.append(registered_count)
            accepted_counts.append(accepted_count)
        # TODO: Убрать отдельно в контекст (можно сделать zip), чтобы не изощряться с получением по индексу
        event.registered_counts = registered_counts
        event.accepted_counts = accepted_counts

        event.registered_count = sum(event.registered_counts)
        event.accepted_count = sum(event.accepted_counts)

    context = {
        'users': users,
        'events': events,
        'users_count': len(users),
        'events_count': len(events),
    }
    return render(request, 'stats/stat.html', context)


# users statistic
def user_stat(request):
    users = User.objects.order_by('email')
    context = {
        'users_list': users,
    }
    return render(request, 'stats/user_stat.html', context)


# detail user statistic
def user_detail(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    return render(request, 'stat/user_detail.html', {'user': user})


# events statistic
def event_stat(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    users_count = User.objects.filter(tracks__event=event_id).count()

    context = {
        'event': event,
        'users_count': users_count,
    }
    return render(request, 'stats/event_stat.html', context)


def import_excel(request):
    if request.method == "POST":
        print(request.FILES)
        excel_file = request.FILES["excel_file"]
        excel_import_service = ExcelImportService()
        excel_import_service.import_excel(excel_file)
        messages.add_message(request, messages.INFO, 'Your excel file has been imported')
        return redirect("..")
    form = ExcelImportForm()
    payload = {"form": form}
    return render(
        request, "core/excel_form.html", payload
    )
