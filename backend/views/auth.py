from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import HttpRequest
from django.utils.dateparse import parse_date

from backend.models import StudentProfile, SchoolProfile, School, Ingredient, MealItem
from backend.views.common import err_response, ok_response, process_post_dict, apply_conversions, pk_converter, \
    without_keys


def view_register_student(request):
    props = process_post_dict(StudentProfile, request.POST, ['meals', 'ban', 'favour', 'allergies'])
    try:
        props = apply_conversions(props, {
                'school': pk_converter(School),
                'birthdate': parse_date,
                'height': float,
                'weight': float,
                'meal_length': float,
                'grad_year': int,
                'ban': pk_converter(MealItem),
                'favour': pk_converter(MealItem),
                'allergies': pk_converter(Ingredient)
            }
        )
    except (School.DoesNotExist, ValueError) as e:
        return err_response(str(e))

    # print(props)

    user = None
    profile = None
    try:
        user = User.objects.create_user(
            username=request.POST.get('email'),
            email=request.POST.get('email'),
            password=request.POST.get('password')
        )
        user.save()
        print(user.__dict__)

        profile = StudentProfile(**without_keys(props, ['ban', 'favour', 'allergies']), user=user)
        profile.full_clean()
        profile.save()

        # Add manytomany fields
        for prop in ['ban', 'favour', 'allergies']:
            getattr(profile, prop).add(*props[prop])
        profile.save()

        return ok_response()
    except (ValidationError, IntegrityError) as e:
        # cleanup
        if user and user.id: user.delete()
        if profile and profile.id: profile.delete()

        # handle exception
        if type(e) == IntegrityError:
            if str(e).find('UNIQUE contraint failed') != -1:
                return err_response(str(e))
            else:
                raise e

        return err_response(str(e))


def view_login(request):
    if request.user.is_authenticated:
        return err_response('Already authenticated')

    email = request.POST.get('email', '')
    password = request.POST.get('password', '')
    auth_type = request.POST.get('type', None)

    try:
        if auth_type == 'school':
            user_obj = SchoolProfile.objects.get(user__username=email, user__password=password).user
        elif auth_type == 'student':
            user_obj = StudentProfile.objects.get(user__username=email, user__password=password).user
        else:
            return err_response('Invalid auth type, should be \'school\' or \'student\'')
    except StudentProfile.DoesNotExist as e:
        return err_response(str(e))

    if user_obj:
        login(request, user_obj)
        return ok_response()
    else:
        return err_response('Invalid email + password combination')


def view_logout(request: HttpRequest):
    if request.user.is_authenticated:
        logout(request)
        return ok_response()
    else:
        return err_response('Not authenticated')
