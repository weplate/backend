from rest_framework import viewsets, serializers
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from backend.algorithm import nutritional_info_for, LARGE_PORTION_MAX, MIN_FILL, SMALL_PORTION_MAX
from backend.models import StudentProfile, MealItem, MealSelection
from backend.views.api.info import ReadNutritionalInfoSerializer
from backend.views.common import IsStudent


class NutritionalRequirementsViewSet(viewsets.ViewSet):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated, IsStudent]

    def list(self, request):
        profile = StudentProfile.objects.get(user=request.user)
        return Response(ReadNutritionalInfoSerializer(nutritional_info_for(profile)).data)


class PortionRequestSerializer(serializers.Serializer):
    small1 = serializers.PrimaryKeyRelatedField(queryset=MealItem.objects.all())
    small2 = serializers.PrimaryKeyRelatedField(queryset=MealItem.objects.all())
    large = serializers.PrimaryKeyRelatedField(queryset=MealItem.objects.all())


class SuggestViewSet(viewsets.ViewSet):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated, IsStudent]

    @action(methods=['GET'], detail=True)
    def items(self, request: Request, pk: int):
        meal = get_object_or_404(MealSelection, pk=pk)

    @action(methods=['GET'], detail=False)
    def portions(self, request: Request):
        req_ser = PortionRequestSerializer(data=request.query_params)
        small1 = req_ser.validated_data['small1']
        small2 = req_ser.validated_data['small2']
        large = req_ser.validated_data['large']

        tmp_sh = SMALL_PORTION_MAX * MIN_FILL
        tmp_lh = LARGE_PORTION_MAX * MIN_FILL

        return Response({
            'small1': {
                'volume': tmp_sh,
                'weight': tmp_sh * small1.density()
            },
            'small2': {
                'volume': tmp_sh,
                'weight': tmp_sh * small2.density()
            },
            'large': {
                'volume': tmp_lh,
                'weight': tmp_lh * large.density()
            },
            'quality': 69
        })
