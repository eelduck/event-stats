from django.contrib import admin
from django import forms
from django.db.models import Count, QuerySet
from django.shortcuts import redirect, render
from django.urls import path

from core.utils import ExportCsvMixin
from event_stats_app.models import Event, Track, TrackChoice, Feedback, ParticipantStatus


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
    list_display = ('title', 'event', 'participants_count', 'attached_task_count', 'accepted_count')
    list_filter = ('title', 'event')
    search_fields = ('title',)

    def get_queryset(self, request):
        queryset: QuerySet = super().get_queryset(request)
        queryset: QuerySet = queryset.annotate(
            _participants_count=Count('participants', distinct=True),
        )
        return queryset

    def participants_count(self, obj) -> int:
        """
        Подсчет количество участников (заявок) в треке
        """
        return obj._participants_count

    # TODO: Починить сортировку
    # Сортировка не работает, возможно проблема из-за django-bootstrap4
    # https://stackoverflow.com/questions/45744315/django-admin-bool-object-has-no-attribute-startswith
    # @admin.display(ordering=True)
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

    def _filter_track_choices_by(self, obj, status) -> QuerySet:
        """
        Фильтрация выбора треков (участников трека) по статусу
        """
        return TrackChoice.objects.filter(track_id=obj.id, status=status)

    # @admin.display(ordering=True, boolean=False)
    def accepted_count(self, obj) -> int:
        """
        Количество участников со статусом ACCEPTED
        """
        accepted: QuerySet = self._filter_track_choices_by(obj, ParticipantStatus.ACCEPTED)
        return accepted.count()


# TODO: Узнать как делать фильтрацию (отображать только треки, выбранные пользователем)
class TaskUrlForm(forms.ModelForm):
    class Meta:
        model = TrackChoice
        # fields = ['participant', 'track', 'task_url']
        exclude = ['change_time', 'status']

    task_url = forms.URLField(
        max_length=500,
        widget=forms.TextInput,
        help_text='Введите ссылку на тестовое задание',
        label='Ссылка на тестовое задание',
    )


# TODO: Добавить кастомную фильтрацию по дате
@admin.register(TrackChoice)
class TrackChoiceAdmin(admin.ModelAdmin):
    change_list_template = 'event_stats_app/track_choice_changelist.html'

    list_display = ('participant', 'track', 'status')
    list_filter = ('status', 'track__title', 'track__event', 'track__event__date')
    search_fields = ('participant__email', 'track__title')

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('add-link-to-task/', self.add_link_to_task),
        ]
        return my_urls + urls

    def add_link_to_task(self, request):
        """
        Добавление ссылки на тестовое и изменение статуса на ON_REVIEW
        """
        if request.method == 'POST':
            # TODO: Узнать как лучше обрабатывать форму
            form = TaskUrlForm(request.POST)
            # https://stackoverflow.com/questions/4308527/django-model-form-object-has-no-attribute-cleaned-data
            # Вызов form.is_valid для появления form.cleaned_data
            form.is_valid()
            track = form.cleaned_data.get('track')
            participant = form.cleaned_data.get('participant')
            track_choice = TrackChoice.objects.get(participant_id=participant.id, track_id=track.id)
            track_choice.task_url = form.data.get('task_url')
            track_choice.status = ParticipantStatus.ON_REVIEW
            track_choice.save()
            return redirect('..')
        form = TaskUrlForm()
        payload = {'form': form}
        return render(request, 'event_stats_app/task_url_form.html', payload)


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
