# List of properties to write
from django.core.exceptions import ValidationError
from rest_framework import serializers, viewsets
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.models import StudentProfile, School, MealItem, Ingredient
from backend.views.common import auth_endpoint, err_response, ok_response, json_response, IsStudent, update_object


class ReadSettingsSerializer(serializers.ModelSerializer):
    class S_MealItem(serializers.ModelSerializer):
        class Meta:
            model = MealItem
            exclude = ['school', 'graphic']

    class S_Ingredient(serializers.ModelSerializer):
        class Meta:
            model = Ingredient
            exclude = ['school']

    class Meta:
        model = StudentProfile
        exclude = ['user']

    ban = S_MealItem(many=True)
    favour = S_MealItem(many=True)
    allergies = S_Ingredient(many=True)


class UpdateSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        exclude = ['user', 'id']
        required = False


class SettingsViewSet(viewsets.ViewSet):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated, IsStudent]

    # We don't actually want to list anything- we want one object
    def list(self, request):
        profile = StudentProfile.objects.get(user=request.user)
        return Response(ReadSettingsSerializer(profile).data)

    @action(detail=False, methods=['post'], url_path='update')
    def settings_update(self, request):
        serialized_data = UpdateSettingsSerializer(data=request.data, partial=True)
        serialized_data.is_valid(raise_exception=True)
        profile = StudentProfile.objects.get(user=request.user)
        upd = update_object(serialized_data, profile)

        return Response({'detail': f'Updated fields {upd}'})
