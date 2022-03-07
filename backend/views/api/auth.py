from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import IntegrityError
from django.urls import reverse
from rest_framework import serializers
from rest_framework.authtoken.admin import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from backend.models import StudentProfile

import re

from backend.utils import IsStudent


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
def check_email_view(_, email):
    if not re.match(r'^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$', email):
        return Response({'detail': 'Invalid email'})

    if User.objects.filter(username=email).exists():
        return Response({'detail': 'Email already taken'})

    return Response({'detail': 'Email ok'})


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
