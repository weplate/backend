import sendgrid
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from rest_framework import permissions, serializers
from rest_framework.exceptions import APIException
from sendgrid.helpers.mail import *


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
        return request.user.studentprofile is not None


class IsVerified(permissions.BasePermission):
    message = 'Must have verified email'

    def has_permission(self, request, view):
        return request.user.studentprofile.is_verified


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


def send_html_email(recipient: str, subject: str, html_message: str):
    """
    Sends an HTML content email to the recipient using SendGrid, email is sent from SENDGRID_EMAIL_SENDER email setting
    @param recipient: Email address of recipient
    @param subject: Subject of email
    @param html_message: HTML content of the message
    @return: The HTTP response after trying to send the email
    """
    sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
    from_email = Email(settings.SENDGRID_EMAIL_SENDER)
    to_email = To(recipient)
    content = Content('text/html', html_message)
    mail = Mail(from_email, to_email, subject, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    return response
