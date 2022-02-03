from django.contrib.auth import login, logout
from django.http import HttpRequest

from backend.models import StudentProfile, SchoolProfile
from backend.views.common import err_response, ok_response


def view_login(request):
    if request.user.is_authenticated():
        return err_response('Already authenticated')

    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    auth_type = request.POST.get('type', None)

    if auth_type == 'school':
        user_obj = SchoolProfile.objects.get(user__username=username, user__password=password).user
    elif auth_type == 'student':
        user_obj = StudentProfile.objects.get(user__username=username, user__password=password).user
    else:
        return err_response('Invalid auth type, should be \'school\' or \'student\'')

    if user_obj:
        login(request, user_obj)
        return ok_response()
    else:
        return err_response('Invalid username/password combination')


def view_logout(request: HttpRequest):
    if request.user.is_authenticated():
        logout(request)
        return ok_response()
    else:
        return err_response('Not authenticated')
