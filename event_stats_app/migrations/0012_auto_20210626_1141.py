# Generated by Django 3.2.4 on 2021-06-26 06:41

from django.db import migrations
from django.contrib.auth.models import Group


def append_group(apps, schema_editor):
    groups = (
        {"name": "Администратор"},
        {"name": "Ментор"},
        {"name": "Участник"},
    )
    for group in groups:
        model = Group(name=group["name"])
        # model = Group(*group)
        model.save()


class Migration(migrations.Migration):
    dependencies = [
        ('event_stats_app', '0011_auto_20210626_1138'),
    ]

    operations = [
        migrations.RunPython(append_group),
    ]
