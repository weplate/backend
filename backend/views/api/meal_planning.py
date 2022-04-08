import datetime

from rest_framework import viewsets, serializers
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from backend.algorithm.item_choice import MealItemSelector
from backend.algorithm.portion import SimulatedAnnealing
from backend.algorithm.requirements import nutritional_info_for
from backend.models import StudentProfile, MealItem, MealSelection
from backend.utils import IsStudent


class NutritionalRequirementsViewSet(viewsets.ViewSet):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated, IsStudent]

    def list(self, request):
        profile = StudentProfile.objects.get(user=request.user)
        lo, hi = nutritional_info_for(profile)
        return Response({
            'lo': lo.as_dict(),
            'hi': hi.as_dict()
        })


class PortionRequestSerializer(serializers.Serializer):
    small1 = serializers.PrimaryKeyRelatedField(queryset=MealItem.objects.all(), many=True)
    small2 = serializers.PrimaryKeyRelatedField(queryset=MealItem.objects.all(), many=True)
    large = serializers.PrimaryKeyRelatedField(queryset=MealItem.objects.all(), many=True)
    large_max_volume = serializers.FloatField()
    small_max_volume = serializers.FloatField()


class ChoiceRequestSerializer(serializers.Serializer):
    large_max_volume = serializers.FloatField()
    small_max_volume = serializers.FloatField()


class SuggestViewSet(viewsets.ViewSet):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated, IsStudent]

    def list(self, _):
        return Response({'detail': 'page either suggest/<meal_id>/items or suggest/portions!'})

    def retrieve(self, _, pk=None):
        return Response({'detail': 'You\'re paging the detail=True endpoint, please page suggest/<meal_id>/items or suggest/portions!'})

    @action(methods=['get'], detail=True)
    def items(self, request: Request, pk=None):
        meal = get_object_or_404(MealSelection, pk=pk)
        profile = StudentProfile.objects.get(user=request.user)
        ser = ChoiceRequestSerializer(data=request.query_params)
        ser.is_valid(raise_exception=True)

        alg = MealItemSelector(meal, profile, ser.validated_data['large_max_volume'], ser.validated_data['small_max_volume'])
        alg.run_algorithm()

        return Response(alg.result_obj())

    @action(methods=['get'], detail=False)
    def portions(self, request: Request):
        profile = StudentProfile.objects.get(user=request.user)
        req_ser = PortionRequestSerializer(data=request.query_params)
        req_ser.is_valid(raise_exception=True)
        small1 = req_ser.validated_data['small1']
        small2 = req_ser.validated_data['small2']
        large = req_ser.validated_data['large']

        algo = SimulatedAnnealing(profile, large, small1, small2,
                                  req_ser.validated_data['large_max_volume'], req_ser.validated_data['small_max_volume'])
        algo.run_algorithm()

        return Response(algo.result_obj())
