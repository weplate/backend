from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import HttpRequest
from django.utils.dateparse import parse_date

from backend.models import StudentProfile, SchoolProfile, School, Ingredient, MealItem
from backend.views.common import err_response, ok_response, process_post_dict, apply_conversions, pk_converter, \
    without_keys


# def view_login(request):
#     if request.user.is_authenticated:
#         return err_response('Already authenticated')
#
#     email = request.POST.get('email', '')
#     password = request.POST.get('password', '')
#     auth_type = request.POST.get('type', None)
#
#     try:
#         auth_user = authenticate(username=email, password=password)
#         if auth_user is None:
#             return err_response('Invalid login')
#
#         if auth_type == 'school':
#             user_obj = SchoolProfile.objects.get(user=auth_user).user
#         elif auth_type == 'student':
#             user_obj = StudentProfile.objects.get(user=auth_user).user
#         else:
#             return err_response('Invalid auth type, should be \'school\' or \'student\'')
#     except StudentProfile.DoesNotExist as e:
#         return err_response(str(e))
#
#     if user_obj:
#         login(request, user_obj)
#         return ok_response()
#     else:
#         return err_response('Login does not match school or student account')
#
#
# def view_logout(request: HttpRequest):
#     if request.user.is_authenticated:
#         logout(request)
#         return ok_response()
#     else:
#         return err_response('Not authenticated')
