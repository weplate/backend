from random import sample

from rest_framework import viewsets, serializers
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from backend.algorithm import nutritional_info_for, \
    LARGE_PORTION, simulated_annealing
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


TEST_COMBO_TRIES = 50
COMBOS_NEEDED = 3


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

        large_items = meal.items.filter(category=MealItem.PROTEIN)
        small1_items = meal.items.filter(category=MealItem.VEGETABLE)
        small2_items = meal.items.filter(category=MealItem.GRAINS)
        large_category = MealItem.PROTEIN
        small1_category = MealItem.VEGETABLE
        small2_category = MealItem.GRAINS

        if LARGE_PORTION[profile.health_goal] == MealItem.VEGETABLE:
            large_items, small1_items = small1_items, large_items
            large_category, small1_category = small1_category, large_category
        elif LARGE_PORTION[profile.health_goal] == MealItem.GRAINS:
            large_items, small2_items = small2_items, large_items
            large_category, small2_category = small2_category, large_category

        num_to_pick = min(TEST_COMBO_TRIES, len(large_items), len(small1_items), len(small2_items))
        item_choices = list(zip(sample(list(large_items.all()), k=num_to_pick),
                                sample(list(small1_items.all()), k=num_to_pick),
                                sample(list(small2_items.all()), k=num_to_pick)))

        result_choices = {
            'large': {
                'items': [],
                'category': large_category
            },
            'small1': {
                'items': [],
                'category': small1_category
            },
            'small2': {
                'items': [],
                'category': small2_category
            },
        }

        for l, s1, s2 in sorted(item_choices,
                           key=lambda c: simulated_annealing(c[0], c[1], c[2],
                                                             nutritional_info_for(profile), 0.99, 0.01))[:COMBOS_NEEDED]:
            result_choices['large']['items'].append(l.pk)
            result_choices['small1']['items'].append(s1.pk)
            result_choices['small2']['items'].append(s2.pk)

        return Response(result_choices)

    @action(methods=['get'], detail=False)
    def portions(self, request: Request):
        profile = StudentProfile.objects.get(user=request.user)
        req_ser = PortionRequestSerializer(data=request.query_params)
        req_ser.is_valid(raise_exception=True)
        small1 = req_ser.validated_data['small1']
        small2 = req_ser.validated_data['small2']
        large = req_ser.validated_data['large']

        (large_volume, small1_volume, small2_volume), cost, runtime = \
            simulated_annealing(large, small1, small2, nutritional_info_for(profile))

        return Response({
            'small1': {
                'volume': small1_volume,
                'weight': small1_volume * small1.density()
            },
            'small2': {
                'volume': small2_volume,
                'weight': small2_volume * small2.density()
            },
            'large': {
                'volume': large_volume,
                'weight': large_volume * large.density()
            },
            'quality': {
                'cost': cost,
                'runtime': runtime
            }
        })
