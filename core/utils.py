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

    # models attributes
    event_title_attribute = 'title'
    event_date_attribute = 'date'

    track_title_attribute = 'title'

    user_city_attribute = 'city'
    user_first_name_attribute = 'first_name'
    user_last_name_attribute = 'last_name'
    user_email_attribute = 'email'
    user_phone_number_attribute = 'phone_number'
    user_status_attribute = 'status'

    # track fk columns
    track_event_attribute = 'event_id'

    # track_choice fk columns
    tc_participant_attribute = 'participant_id'
    tc_track_attribute = 'track_id'

    # Columns to create model dataframe
    user_attributes = {
        user_first_name_header: user_first_name_attribute,
        user_last_name_header: user_last_name_attribute,
        user_email_header: user_email_attribute,
        user_phone_number_header: user_phone_number_attribute,
        user_city_header: user_city_attribute
    }

    event_attributes = {
        event_title_header: event_title_attribute,
        event_date_header: event_date_attribute
    }

    track_attributes = {
        track_title_header: track_title_attribute,
        event_title_header: event_title_attribute,
        event_date_header: event_date_attribute
    }
    # tc - track_choice
    tc_attributes = {
        user_email_header: user_email_attribute,
        event_title_header: event_title_attribute,
        event_date_header: event_date_attribute,
        track_title_header: track_title_attribute
    }

    # TODO: поменять структуру данных
    # Columns to import to models
    track_import_attributes = {
        track_title_header: track_title_attribute,
        track_event_attribute: track_event_attribute
    }

    tc_import_attributes = [
        tc_participant_attribute,
        tc_track_attribute,
        user_status_attribute
    ]

    def _convert_columns(self):
        """
        Преобразование колонок к необходимым типам данных
        """
        self.df[self.event_date_header] = self.df[
            self.event_date_header
        ].astype('datetime64')

    def _create_model_df(self, attributes: dict, duplicates_subset=None) -> pd.DataFrame:
        """
        Создаёт датафрейм, из необходимых для модели аттрибутов
        """
        model_df = self.df[attributes.keys()].drop_duplicates(subset=duplicates_subset, keep='last')
        return model_df

    def _create_model_dict(self, attributes: dict, duplicates_subset=None) -> dict:
        model_df = self._create_model_df(attributes, duplicates_subset)
        model_df.rename(columns=attributes, inplace=True)
        model_dict = model_df.to_dict('records')
        pprint(model_dict)
        return model_dict

    # TODO: Допилить функционал загрузки трека и выбора трека
    def _create_track_dict(self):
        def get_event_id(row):
            pprint(row)
            return Event.objects.get(
                title=row[self.event_title_header],
                date=row[self.event_date_header]).id
        track_df = self._create_model_df(self.track_attributes)
        track_df[self.track_event_attribute] = track_df.apply(lambda row: get_event_id(row), axis=1)

        # TODO: Убрать дублирвоание кода
        track_df.rename(columns=self.track_import_attributes, inplace=True)
        track_dict = track_df[self.track_import_attributes.values()].to_dict('records')
        return track_dict

    def _create_tc_dict(self):
        def get_participant_id(row):
            pprint(row)
            return User.objects.get(email=row[self.user_email_header]).id

        tc_df = self._create_model_df(self.tc_attributes)
        tc_df[self.tc_participant_attribute] = tc_df.apply(
            lambda row: get_participant_id(row), axis=1)

        def get_track_id(row):
            event_id = Event.objects.get(
                title=row[self.event_title_header],
                date=row[self.event_date_header]).id
            return Track.objects.get(
                event_id=event_id,
                title=row[self.track_title_header]
            ).id

        tc_df[self.tc_track_attribute] = tc_df.apply(
            lambda row: get_track_id(row), axis=1)

        tc_df[self.user_status_attribute] = ParticipantStatus.REGISTERED

        # TODO: Убрать дублирвоание кода
        tc_dict = tc_df[self.tc_import_attributes].to_dict('records')
        return tc_dict

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
        self._add_objects(User, users)

        events = self._create_model_dict(
            attributes=self.event_attributes,
        )
        self._add_objects(Event, events)

        tracks = self._create_track_dict()
        self._add_objects(Track, tracks)

        track_choices = self._create_tc_dict()
        self._add_objects(TrackChoice, track_choices)

    def import_excel(self, excel_file: InMemoryUploadedFile):
        self.df = pd.read_excel(excel_file)
        self._add_all_data()
