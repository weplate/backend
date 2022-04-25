import datetime
import functools
from dataclasses import dataclass

import requests
from django.conf import settings
from django.core.cache import cache
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.urls import path
from rest_framework.authtoken.models import Token

from backend.models import MealSelection

JOB_LOG_CACHE_KEY = 'job_log'
PUSH_LAST_MEAL_CACHE_KEY = 'last_meal_push_notifed'


@dataclass
class JobResult:
    url: str
    response: str
    timestamp: datetime.datetime


def add_job_result(url: str, response: str):
    """
    Adds a job result object to the log of job results, stored in the cache.  This is cleared every 7 days
    @param url: URL of the job
    @param response: Response message of the job
    @return: None
    """
    lst = cache.get_or_set(JOB_LOG_CACHE_KEY, [])
    lst.insert(0, JobResult(url, response, datetime.datetime.now()))
    lst = lst[len(lst) - settings.JOB_LOG_MAX_SIZE:]
    cache.set(JOB_LOG_CACHE_KEY, lst)


def get_job_results() -> list[JobResult]:
    """
    @return: The list of job results, in order of addition (earliest to latest).  Max # of results determined by
    settings.JOB_LOG_MAX_SIZE
    """
    return cache.get_or_set(JOB_LOG_CACHE_KEY, [])


def appengine_job(view_fun):
    @functools.wraps(view_fun)
    def wrapper(request: WSGIRequest, *args, **kwargs):
        if not settings.PROD or request.headers.get('X-Appengine-Cron', None) == 'true':
            response: HttpResponse = view_fun(request, *args, **kwargs)
            add_job_result(request.path, str(response.content, 'utf8'))
            return response
        else:
            return HttpResponse('Job access denied')

    return wrapper


@appengine_job
def clear_tokens(_):
    queryset = Token.objects.all()
    count = queryset.count()
    queryset.delete()
    return HttpResponse(f'Removed {count} tokens')


@appengine_job
def clear_cache(_):
    cache.clear()
    return HttpResponse('Cleared Cache')


def post_push_request(title: str, body: str, data: dict[str, any]):
    """
    Sends a notification to all devices using the app through Expo.  Uses EXPO_PUSH_TOKEN setting.
    @param title: The title of the push notification
    @param body: The body of the push notification
    @param data: A dict, which should be JSON-serializable (i.e. you can do json.dumps(data))
    @return: The response of the request
    """

    return requests.post(url='https://exp.host/--/api/v2/push/send/',
                         json={
                             'to': settings.EXPO_PUSH_TOKEN,
                             'title': title,
                             'body': body,
                             'data': data
                         })


@appengine_job
def send_push(_):
    prev_time = max(cache.get_or_set(PUSH_LAST_MEAL_CACHE_KEY, datetime.datetime.utcfromtimestamp(0)),
                    datetime.datetime.utcnow())
    next_meal = None

    if next_meal := MealSelection.objects.filter(timestamp__gt=prev_time).order_by('timestamp').first():
        prev_time = next_meal.timestamp
        post_push_request(
            'your mom meal: ' + next_meal.name,
            'your mom mom',
            {
                'your': 'mom'
            }
        )

    cache.set(PUSH_LAST_MEAL_CACHE_KEY, prev_time)

    return HttpResponse(f'Sent push notification for "{next_meal.name}"' if next_meal else 'No future meals exist, could not send notification')


urlpatterns = [
    path('clear_tokens/', clear_tokens, name='clear_tokens'),
    path('clear_cache/', clear_cache, name='clear cache'),
    path('send_push/', send_push, name='send_push'),
]