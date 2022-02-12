from rest_framework import views, viewsets
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.algorithm import nutritional_info_for
from backend.models import StudentProfile
from backend.views.api.info import ReadNutritionalInfoSerializer
from backend.views.common import IsStudent


class NutritionalRequirementsViewSet(viewsets.ViewSet):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated, IsStudent]

    def list(self, request):
        profile = StudentProfile.objects.get(user=request.user)
        return Response(ReadNutritionalInfoSerializer(nutritional_info_for(profile)).data)