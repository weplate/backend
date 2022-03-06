import datetime

from django.core.cache import cache
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
        return Response(nutritional_info_for(profile).as_dict())


class PortionRequestSerializer(serializers.Serializer):
    small1 = serializers.PrimaryKeyRelatedField(queryset=MealItem.objects.all())
    small2 = serializers.PrimaryKeyRelatedField(queryset=MealItem.objects.all())
    large = serializers.PrimaryKeyRelatedField(queryset=MealItem.objects.all())


TEST_COMBO_TRIES = 100
COMBOS_NEEDED = 3
CACHE_TIMEOUT = datetime.timedelta(hours=6).total_seconds()


class SuggestViewSet(viewsets.ViewSet):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated, IsStudent]

    def list(self, _):
        return Response({'detail': 'page either suggest/<meal_id>/items or suggest/portions!'})

    def retrieve(self, _, pk=None):
        return Response({'detail': 'You\'re paging the detail=True endpoint, please page suggest/items'})

    @action(methods=['get'], detail=True)
    def items(self, request: Request, pk=None):
        meal = get_object_or_404(MealSelection, pk=pk)
        profile = StudentProfile.objects.get(user=request.user)
        cache_key = f'weplate_suggest_items_meal{meal.id}_profile{profile.id}'
        if _cache_res := cache.get(cache_key):
            return Response(_cache_res)

        alg = MealItemSelector(meal, profile)
        alg.run_algorithm()

        cache.set(cache_key, alg.result_dict, CACHE_TIMEOUT)
        return Response(alg.result_dict)

    @action(methods=['get'], detail=False)
    def portions(self, request: Request):
        profile = StudentProfile.objects.get(user=request.user)
        req_ser = PortionRequestSerializer(data=request.query_params)
        req_ser.is_valid(raise_exception=True)
        small1 = req_ser.validated_data['small1']
        small2 = req_ser.validated_data['small2']
        large = req_ser.validated_data['large']

        algo = SimulatedAnnealing(profile, large, small1, small2)
        algo.run_algorithm()

        return Response({
            'small1': {
                'volume': algo.small1_volume,
                'weight': algo.small1_volume * small1.density()
            },
            'small2': {
                'volume': algo.small2_volume,
                'weight': algo.small2_volume * small2.density()
            },
            'large': {
                'volume': algo.large_volume,
                'weight': algo.large_volume * large.density()
            },
            'quality': {
                'cost': algo.final_cost,
                'runtime': algo.runtime
            }
        })
