from django.core.mail import send_mail
from django.urls import reverse
from rest_framework import serializers
from rest_framework.authtoken.admin import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from backend.models import EmailVerificationToken, StudentProfile
from backend.utils import IsStudent


class ResetPasswordPostSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=256)


@api_view(['post'])
@permission_classes([IsAuthenticated, IsStudent])
def verify_email_post(request: Request):
    token_obj = EmailVerificationToken.objects.create_token(request.user)
    verify_url = request.build_absolute_uri(reverse('verify_email_get', args=(request.user.id, token_obj.token)))
    send_mail(
        subject=f'WePlate Email Verification',
        message='',
        html_message=f'Visit <a href="{verify_url}">this link</a> to verify your email!',
        from_email=None,
        recipient_list=[request.user.email],
    )
    return Response({'detail': 'ok'})


@api_view(['get'])
def verify_email_get(request: Request, user_id: int, token: str):
    user = User.objects.get(id=user_id)
    if not user:
        return Response('User not found')
    else:
        profile = StudentProfile.objects.get(user=user)
        if profile:
            token_obj = EmailVerificationToken.objects.get_token(user)
            if token_obj:
                if token_obj.token != token:
                    return Response('Incorrect token')
                else:
                    user.is_active = True
                    user.save()
                    return Response(f'Email verified for user {user.username}! You may now login using the app!')
            else:
                return Response('No token found')
        else:
            return Response('User is not a student')


@api_view(['post'])
def reset_password_post(request: Request):
    pass


@api_view(['get'])
def reset_password_get(request: Request, user_id: int, token: str):
    pass
