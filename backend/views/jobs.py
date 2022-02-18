import functools

from django.http import HttpResponse
from django.urls import path
from rest_framework.authtoken.models import Token


def appengine_job(view_fun):
    @functools.wraps(view_fun)
    def wrapper(request, *args, **kwargs):
        if request.headers.get('X-Appengine-Cron', None) == 'true':
            return view_fun(request, *args, **kwargs)
        else:
            return HttpResponse('Job access denied')

    return wrapper


@appengine_job
def clear_tokens(_):
    queryset = Token.objects.all()
    count = queryset.count()
    queryset.delete()
    return HttpResponse(f'Removed {count} tokens')


urlpatterns = [
    path('clear_tokens/', clear_tokens, name='clear_tokens')
]
