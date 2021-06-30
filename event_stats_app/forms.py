from django import forms

from event_stats_app.models import TrackChoice


# TODO: Узнать как делать фильтрацию (отображать только треки, выбранные пользователем)
# Сделать кастомный виджет на поле в котором динамически фильтровать через JS
class TaskUrlForm(forms.ModelForm):
    class Meta:
        model = TrackChoice
        # fields = ['participant', 'track', 'task_url']
        exclude = ['change_time', 'status']


class TaskUrlForm1(forms.ModelForm):
    class Meta:
        model = TrackChoice
        # fields = ['participant', 'track', 'task_url']
        exclude = ['change_time', 'status', 'track', 'task_url']


class TaskUrlForm2(forms.ModelForm):
    class Meta:
        model = TrackChoice
        # fields = ['participant', 'track', 'task_url']
        exclude = ['change_time', 'status', 'participant']

    def __init__(self, *args, **kwargs):
        # TODO: Нужно как-то получить выбор с предыдущего шага
        super().__init__(*args, **kwargs)
        # TODO: Нужно отфильтровать по participant,
        # self.fields['track'].queryset = TrackChoice.objects.filter(participant=)