from django.contrib import admin, messages
from django.forms import forms
from django.urls import path
from core.models import CustomUser
from core.utils import ExportCsvMixin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin


class ExcelImportForm(forms.Form):
    excel_file = forms.FileField()


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin, ExportCsvMixin):
    add_form_template = 'admin/auth/user/add_form.html'
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
    list_filter = ('is_staff', 'is_superuser', 'groups', 'city')
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions', 'interested',)
    actions = ['subscribe_to_participant', 'export_as_csv']

    def get_urls(self):
        return [
                   path(
                       '<id>/password/',
                       self.admin_site.admin_view(self.user_change_password),
                       name='auth_user_password_change',
                   ),
               ] + super().get_urls()

    @admin.action(description='Подписаться выбранных участников')
    def subscribe_to_participant(self, request, queryset):
        for participant in queryset:
            participant.interested.add(
                CustomUser.objects.get(email=request.user.email))
        messages.add_message(request, messages.INFO,
                             f'Подписка на участников прошла успешно')
