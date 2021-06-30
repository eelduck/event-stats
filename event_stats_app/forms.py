from django import forms

from event_stats_app.models import TrackChoice
from django.utils.translation import gettext_lazy as _


# TODO: Узнать как делать фильтрацию (отображать только треки, выбранные пользователем)
# Сделать кастомный виджет на поле в котором динамически фильтровать через JS
class TaskUrlForm(forms.ModelForm):
    class Meta:
        model = TrackChoice
        exclude = ['change_time', 'status']


class TaskUrlForm1(forms.ModelForm):
    class Meta:
        model = TrackChoice
        exclude = ['change_time', 'status', 'track', 'task_url']


class TaskUrlForm2(forms.Form):
    track_choice = forms.ModelChoiceField(queryset=None, label=_('Выбор трека'))
    task_url = forms.CharField(max_length=255, label=_('Ссылка на тестовое задание'))
