from django.contrib.auth.models import User
from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.exceptions import APIException
from rest_framework.response import Response

from backend.models import StudentProfile

import re


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
        profile_data = ProfileSerializer(data=request.data | {'user': new_user.id})
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
