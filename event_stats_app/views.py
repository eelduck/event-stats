from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404, render
from .models import User
from .models import Event

# users statistic
def userstat(request):
    users = User.objects.order_by('email')
    template = loader.get_template('stats/userstat.html')
    context = {
        'users_list': users,
    }
    return HttpResponse(template.render(context, request))

# detail user statistic
def userdetail(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    return render(request, 'stat/userdetail.html', {'user': user})


# events statistic
def eventstat(request):
    events = Event.objects.order_by('id')
    template = loader.get_template('stats/eventstat.html')
    context = {
        'events_list': events,
    }
    return HttpResponse(template.render(context, request))


# detail event
def eventdetail(request, event_id):
    event = get_object_or_404(User, pk=event_id)
    return render(request, 'stat/eventdetail.html', {'event': event})


# tracks statistic
def eventstat(request):
    events = Event.objects.order_by('id')
    template = loader.get_template('stats/eventstat.html')
    context = {
        'events_list': events,
    }
    return HttpResponse(template.render(context, request))


# detail event
def eventdetail(request, event_id):
    event = get_object_or_404(User, pk=event_id)
    return render(request, 'stat/eventdetail.html', {'event': event})