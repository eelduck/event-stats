import csv
from pprint import pprint

from typing import List

import pandas as pd
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import Model

from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _

from event_stats_app.models import User, Event, Track, TrackChoice, ParticipantStatus


class ExportCsvMixin:
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = _("Export Selected")


class ImportCsvMixin:
    pass


class ExcelImportService:
    """
    Этот класс реализует логику работы с excel файлом и добавление
    данных из него в модели
    """
    # excel columns
    event_title_header = 'Событие'
    event_date_header = 'Дата'
    track_title_header = 'Трэк'
    user_city_header = 'Город'
    user_first_name_header = 'Имя'
    user_last_name_header = 'Фамилия'
    user_email_header = 'E-mail'
    user_phone_number_header = 'Номер телефона'
    user_status_header = 'Статус'

    # track fk columns
    track_event = 'event_id'

    # track_choice fk columns
    track_choice_participant = 'participant_id'
    track_choice_track = 'track_id'
    track_choice_status = 'status'

    columns_to_rename = {
        event_title_header: 'title',
        event_date_header: 'date',
        track_title_header: 'title',
        user_first_name_header: 'first_name',
        user_last_name_header: 'last_name',
        user_email_header: 'email',
        user_phone_number_header: 'phone_number'
    }

    # Columns to create model dataframe
    user_attributes = [
        user_first_name_header,
        user_last_name_header,
        user_email_header,
        user_phone_number_header,
        user_city_header
    ]

    event_attributes = [
        event_title_header,
        event_date_header
    ]

    track_attributes = [
        track_title_header,
        event_title_header,
        event_date_header
    ]

    track_choice_attributes = [
        user_email_header,
        event_title_header,
        event_date_header,
        track_title_header
    ]

    # Columns to import to models
    user_import_attributes = user_attributes
    event_import_attributes = event_attributes
    track_import_attributes = [
        columns_to_rename[track_title_header],
        track_event
    ]
    track_choice_import_attributes = [
        columns_to_rename[track_title_header],
        track_event
    ]

    def _convert_columns(self):
        """
        Преобразование колонок к необходимым типам данных
        """
        self.df[self.event_date_header] = self.df[
            self.event_date_header
        ].astype('datetime64')

    def _create_model_df(self, attributes: List[str], duplicates_subset=None) -> pd.DataFrame:
        """
        Создаёт датафрейм, из необходимых для модели аттрибутов
        """
        model_df = self.df[attributes].drop_duplicates(subset=duplicates_subset, keep='last')
        model_df.rename(columns=self.columns_to_rename, inplace=True)
        return model_df

    def _create_model_dict(self, attributes: List[str], duplicates_subset=None) -> dict:
        model_df = self._create_model_df(attributes, duplicates_subset)
        model_dict = model_df.to_dict('records')
        return model_dict

    # TODO: Допилить функционал загрузки трека и выбора трека
    def _create_track_dict(self):
        pass

    # TODO: Отрефакторить функцию
    @staticmethod
    def _add_objects(model: Model, entities_to_add: list[dict], wipe: bool = False):
        """
        Добавление экземпляров модели
        data: Данные для добавление
        model: django.db.models - модель, в которую будут добавляться данные
        wipe: флаг очистки всех сущностней модели
        """
        qs = model.objects.all()
        if wipe and qs.count() != 0:
            qs.delete()
        new_entities = []
        if qs.count() == 0:
            for entity in entities_to_add:
                new_entity = model(**entity)
                new_entities.append(new_entity)

            model.objects.bulk_create(new_entities)
        else:
            for entity in entities_to_add:
                new_entity, created = model.objects.get_or_create(**entity)
                if created:
                    new_entity.save()

    # TODO: Возможно вынести эту функцию за пределы класса, т.к. она использует в себе модели из импорта
    def _add_all_data(self):
        """
        Добавляет все данные из экселя в модели
        """
        self._convert_columns()

        users = self._create_model_dict(
            attributes=self.user_attributes,
            duplicates_subset=self.user_email_header
        )
        events = self._create_model_dict(
            attributes=self.event_attributes,
        )
        tracks = self._create_model_dict(
            attributes=self.track_attributes,
        )
        track_choices = self._create_model_dict(
            attributes=self.track_choice_attributes,
        )

        self._add_objects(User, users)
        self._add_objects(Event, events)
        self._add_objects(Track, tracks)
        self._add_objects(TrackChoice, track_choices)

    def import_excel(self, excel_file: InMemoryUploadedFile):
        self.df = pd.read_excel(excel_file)
        self._add_all_data()
