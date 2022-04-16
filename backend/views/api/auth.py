import re
import urllib.parse

from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import IntegrityError
from django.shortcuts import render
from django.template import loader
from django.urls import reverse
from rest_framework import serializers, viewsets
from rest_framework.authtoken.admin import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import APIException
from rest_framework.request import Request
from rest_framework.response import Response

from backend.models import StudentProfile
from backend.models.token import EmailVerificationToken, PasswordResetToken
from backend.utils import send_html_email


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']

    username = serializers.EmailField()


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = '__all__'


@api_view(['POST'])
@permission_classes([])
def register_student_view(request):
    user_data = UserSerializer(data=request.data)
    user_data.is_valid(raise_exception=True)

    try:
        new_user = User.objects.create_user(username=user_data.validated_data['username'],
                                            email=user_data.validated_data['username'],
                                            password=user_data.validated_data['password'])
        new_user.save()
    except IntegrityError as e:
        raise APIException(str(e))

    try:
        profile_data = ProfileSerializer(data=request.data | {'user': new_user.id, 'is_verified': False})
        profile_data.is_valid(raise_exception=True)
        profile_data.save()
    except Exception as e:
        new_user.delete()  # Delete the user if validation otherwise failed
        raise e

    return Response({'detail': f'successfully registered user {new_user.username}'})


@api_view(['GET'])
@permission_classes([])
def check_email_view(_, email):
    if not re.match(r'^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$', email):
        return Response({'detail': 'Invalid email'})

    if User.objects.filter(username=email).exists():
        return Response({'detail': 'Email already taken'})

    return Response({'detail': 'Email ok'})


def user_from_email(email):
    if email is None:
        raise APIException('No email specified')
    if (user := User.objects.filter(username=email).first()) is None:
        raise APIException('Email does not correspond to user')
    return user


class VerifyEmailViewSet(viewsets.ViewSet):
    permission_classes = []

    def create(self, request: Request):
        user = user_from_email(request.data.get('email'))
        token_obj = EmailVerificationToken.objects.create_token(user)
        verify_url = request.build_absolute_uri(reverse('VerifyEmail-list') + '?' + urllib.parse.urlencode({
            'email': user.email,
            'token': token_obj.token
        }))
        send_html_email(
            user.email,
            'WePlate Email Verification',
            loader.get_template('email/email.html').render({
                'action': 'Email Verification',
                'action_verb': 'verify the email',
                'url': verify_url
            }, request)
        )
        return Response({'detail': 'ok'})

    def list(self, request: Request):
        error = None
        try:
            user = user_from_email(request.GET.get('email'))
            if (profile := StudentProfile.objects.filter(user=user).first()) is None:
                raise APIException('User is not a student')
            EmailVerificationToken.objects.process_token(user, request.GET.get('token'))
            profile.is_verified = True
            profile.save()
        except APIException as e:
            error = str(e)

        return render(request, 'email/result.html', {
            'action': 'Email Verification',
            'action_verb': 'email has been verified',
            'email': request.GET.get('email', 'Anonymous User'),
            'error': error
        })


class ResetPasswordViewSet(viewsets.ViewSet):
    permission_classes = []

    def create(self, request: Request):
        if (password := request.data.get('password')) is None:
            raise APIException('No password was specified')
        user = user_from_email(request.data.get('email'))
        token_obj = PasswordResetToken.objects.create_token(user, new_password=password)

        reset_url = request.build_absolute_uri(reverse('ResetPassword-list') + '?' + urllib.parse.urlencode({
            'email': user.email,
            'token': token_obj.token
        }))
        send_html_email(
            user.email,
            'WePlate Password Reset',
            loader.get_template('email/email.html').render({
                'action': 'Password Reset',
                'action_verb': 'reset the password',
                'url': reset_url
            }, request)
        )
        return Response({'detail': 'ok'})

    def list(self, request: Request):
        error = None
        try:
            user = user_from_email(request.GET.get('email'))
            token_obj = PasswordResetToken.objects.process_token(user, request.GET.get('token'))
            user.set_password(token_obj.new_password)
            user.save()
        except APIException as e:
            error = str(e)

        return render(request, 'email/result.html', {
            'action': 'Password Reset',
            'action_verb': 'password has been reset',
            'email': request.GET.get('email', 'Anonymous User'),
            'error': error
        })
