from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404, render
from .models import User
from .models import Event



# statistic
def stat(request):
    users = User.objects.order_by('email')
    events = Event.objects.all()
    template = loader.get_template('stats/stat.html')
    context = {
        'users': users,
        'events': events,
        'userscount': len(users),
        'eventscount': len(events),
    }
    return HttpResponse(template.render(context, request))



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
def eventstat(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    template = loader.get_template('stats/eventstat.html')
    context = {
        'event': event,
    }
    return HttpResponse(template.render(context, request))


