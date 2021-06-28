import pandas as pd
from django.contrib import admin
from django.forms import forms
from django.shortcuts import redirect, render
from django.urls import path
from core.models import User
from core.utils import ExportCsvMixin, ExcelImportService
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin


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
               ] + super().get_urls()

    # def _export_as_csv(self, request):
    #     queryset = None
