from django.core.exceptions import ValidationError
from django.db import models
from rest_framework import permissions, serializers
from rest_framework.exceptions import APIException

from backend.models import StudentProfile


def fetch_or_apiexcept(model, message, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        raise APIException(message)


def fetch_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None


class IsStudent(permissions.BasePermission):
    message = 'Must be authenticated as student user'

    def has_permission(self, request, view):
        return StudentProfile.objects.filter(user=request.user).exists()


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