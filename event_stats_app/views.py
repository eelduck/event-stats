from django.contrib import messages
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from formtools.wizard.views import SessionWizardView

from core.admin import ExcelImportForm
from core.utils import ExcelImportService
from .forms import TaskUrlForm1, TaskUrlForm2
from .models import TrackChoice


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


class AttachUrlWizard(SessionWizardView):
    template_name = 'event_stats_app/task_url_form.html'
    form_list = [TaskUrlForm1, TaskUrlForm2]

    def get_form(self, step=None, data=None, files=None):
        # data: This QueryDict instance is immutable
        form = super().get_form(step, data, files)
        if step is None:
            step = self.steps.current

        if step == '1':
            participant_id = int(self.storage.data.get('step_data').get('0').get('0-participant')[0])
            form.fields['track_choice'].queryset = TrackChoice.objects.filter(participant_id=participant_id)
            return form
        return form

    def done(self, form_list, **kwargs):
        info_step = str(1)
        data = self.get_cleaned_data_for_step(info_step)

        tc = data.get('track_choice')
        task_url = data.get('task_url')
        tc.task_url = task_url
        tc.save()

        messages.add_message(self.request, messages.INFO, _('Ссылка на ТЗ успешно прикреплена'))
        return redirect("..")
