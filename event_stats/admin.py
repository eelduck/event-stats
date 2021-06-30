from django.contrib import admin


# By https://docs.djangoproject.com/en/3.2/ref/contrib/admin/#overriding-the-default-admin-site
class CustomAdminSite(admin.AdminSite):
    site_header = 'Управление мероприятиями'
    site_title = site_header
    index_title = 'Добро пожаловать на портал управления мероприятиями'
