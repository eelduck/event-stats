from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('stat/', views.stat, name='stat'),
    path('stat/user/', views.userstat, name='userstat'),
    path('stat/event/<int:event_id>', views.eventstat, name='eventstat'),
    path('stat/user/<int:user_id>', views.userdetail, name='userdetail'),
]