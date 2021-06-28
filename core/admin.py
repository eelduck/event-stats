import pandas as pd
from django.contrib import admin
from django.contrib.auth.models import Group
from django.forms import forms
from django.shortcuts import redirect, render
from django.urls import path
from core.models import User
from core.utils import ExportCsvMixin, ExcelImportService
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin
from django.apps import apps
from django.contrib.auth import models


def patch_group_label_name():
    """
    Нахождение модели Group в списке всех моделей
    и изменение названия/принадлежности к приложению

    https://stackoverflow.com/questions/28121289/how-to-move-model-to-the-other-section-in-djangos-site-admin
    +
    https://stackoverflow.com/questions/3599524/get-class-name-of-django-model
    """
    models_list = apps.get_models(models)
    # Looks like monkey patching
    group_model_index = 3
    for index, model in enumerate(models_list):
        if model.__name__ == 'Group':
            group_model_index = index
            break

    models_list[group_model_index]._meta.app_label = 'core'


patch_group_label_name()


class ExcelImportForm(forms.Form):
    excel_file = forms.FileField()


@admin.register(User)
class CustomUserAdmin(UserAdmin, ExportCsvMixin):
    add_form_template = 'admin/auth/user/add_form.html'
    change_list_template = 'core/user_changelist.html'
    fieldsets = (
        (None, {'fields': ('password',)}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'city')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Status monitoring'), {'fields': ('interested',)})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'city', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'city')
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)
    actions = ['export_as_csv']

    def get_urls(self):
        return [
                   path(
                       '<id>/password/',
                       self.admin_site.admin_view(self.user_change_password),
                       name='auth_user_password_change',
                   ),
                   # path('export_as_csv/', self._export_as_csv)
                   path('import-excel/', self.import_excel)
               ] + super().get_urls()

    # def _export_as_csv(self, request):
    #     queryset = None

    def import_excel(self, request):
        if request.method == "POST":
            print(request.FILES)
            excel_file = request.FILES["excel_file"]
            excel_import_service = ExcelImportService()
            excel_import_service.import_excel(excel_file)
            self.message_user(request, "Your excel file has been imported")
            return redirect("..")
        form = ExcelImportForm()
        payload = {"form": form}
        return render(
            request, "core/excel_form.html", payload
        )
