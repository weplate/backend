from django.core.exceptions import ValidationError
from django.core.handlers.wsgi import WSGIRequest
from django.db import models
from django.http import JsonResponse

import functools

from rest_framework import permissions, serializers
from rest_framework.exceptions import APIException

from backend.models import StudentProfile


def json_response(data: dict[str, object], error: bool = False, message: str = 'success') -> JsonResponse:
    return JsonResponse(
        data=data | {
            'error': error,
            'message': message
        }
    )


def ok_response(message: str = 'success'):
    return json_response({}, False, message)


def err_response(message: str):
    return json_response({}, True, message)


def auth_endpoint(model):
    """
    Decorator for endpoints that require authentication with profiles
    @param model Profile model
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(request: WSGIRequest, *args, **kwargs):
            if request.user.is_authenticated:
                if model.objects.filter(user__id=request.user.id).exists():
                    return func(request, *args, **kwargs)
                else:
                    return err_response('Not authenticated')
            else:
                return err_response('Not authenticated')

        return wrapper

    return decorator


def pk_converter(model):
    """
    Returns a function that can convert a primary key (or nested list of primary keys into
    objects from some model
    @param model The model to build the converter for
    """

    def converter(obj):
        if type(obj) == list:
            return [converter(x) for x in obj]
        return model.objects.get(pk=int(obj))

    return converter


def process_post_dict(model, post_dict, listify=[]):
    """
    Processes the post dict from a post request into a dictionary ready for DB entry
    @param model Only properties also present in the model will be included
    @param post_dict Usually "request.POST"
    @param listify List of parameters to convert into lists if they're not already lists
    """
    return dict((
        ((k, v) if type(v) == list or k not in listify else (k, [v]))
        for k, v in post_dict.items() if k in model.__dict__
    ))


def apply_conversions(dict_obj: dict, conv_dict: dict) -> dict:
    """
    Applies a set of conversions on a dictionary object
    """
    return dict(((k, conv_dict[k](v)) if k in conv_dict else (k, v)
                 for k, v in dict_obj.items()))


def without_keys(dict_obj: dict, keys: list) -> dict:
    """
    Copies a dictionary and removes the listed keys from it
    """

    res = dict_obj.copy()
    for key in keys:
        if key in res:
            del res[key]
    return res


class IsStudent(permissions.BasePermission):
    message = 'Must be authenticated as student user'

    def has_permission(self, request, view):
        return StudentProfile.objects.filter(user=request.user).exists()


class IsVerified(permissions.BasePermission):
    message = 'Must have verified email'

    def has_permission(self, request, view):
        profile = StudentProfile.objects.get(user=request.user)
        return profile and profile.is_verified


def update_object(serializer: serializers.ModelSerializer, obj: models.Model) -> list:
    # Update model object
    upd = []
    for k, v in serializer.validated_data.items():
        if hasattr(getattr(obj, k), 'set'):  # Many2many field
            getattr(obj, k).set(v)
        else:
            setattr(obj, k, v)
        upd.append(k)

    # Update object in DB
    try:
        obj.full_clean()
        obj.save()
    except ValidationError as e:
        raise APIException(str(e))

    return upd


