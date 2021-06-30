from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404, render
from formtools.wizard.views import SessionWizardView

from core.admin import ExcelImportForm
from core.utils import ExcelImportService
from .forms import TaskUrlForm1, TaskUrlForm2
from .models import User, TrackChoice, ParticipantStatus
from .models import Event
from django.template import Context

from django.utils.translation import gettext_lazy as _


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


class CustomSessionWizardView(SessionWizardView):
    """
    Переопределение функции, а точнее одного поля для передачи дополнительных значений в генерируемые формы
    """

    def render_next_step(self, form, **kwargs):
        """
        This method gets called when the next step/form should be rendered.
        `form` contains the last/current form.
        prev_step_data -
        """
        # get the form instance based on the data from the storage backend
        # (if available).
        next_step = self.steps.next
        new_form = self.get_form(
            next_step,
            data=self.storage.get_step_data(next_step),
            files=self.storage.get_step_files(next_step),
        )
        new_form.prev_step_data = kwargs.get('prev_step_data')
        # change the stored current step
        self.storage.current_step = next_step
        return self.render(new_form, **kwargs)


class AttachUrlWizard(SessionWizardView):
    template_name = 'event_stats_app/task_url_form.html'
    form_list = [TaskUrlForm1, TaskUrlForm2]

    def get_form(self, step=None, data=None, files=None):
        form = super().get_form(step, data, files)

        if step is None:
            step = self.steps.current

        if step == '1':
            step0_form = self.form_list.get(str(0))
            print(step0_form)
            # print(f'{kek=}')
            form.fields['track'].queryset = TrackChoice.objects.all()
        return form

    def done(self, form_list, **kwargs):
        c = Context({
            'form_list': [x.cleaned_data for x in form_list],
            'form_dict': kwargs.get('form_dict'),
            'all_cleaned_data': self.get_all_cleaned_data()
        })
        for form in self.form_list.keys():
            c[form] = self.get_cleaned_data_for_step(form)

        print(c)

        messages.add_message(self.request, messages.INFO, _('Ссылка на ТЗ успешно прикреплена'))
        return redirect("..")
