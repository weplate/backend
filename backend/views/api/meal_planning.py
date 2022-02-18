from rest_framework import viewsets, serializers
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from backend.algorithm import nutritional_info_for, LARGE_PORTION_MAX, MIN_FILL, SMALL_PORTION_MAX, ItemType, \
    LARGE_PORTION
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

    def list(self, _):
        return Response({'detail': 'page either suggest/items or suggest/portions!'})

    def retrieve(self, _, pk=None):
        return Response({'detail': 'You\'re paging the detail=True endpoint, please page suggest/items'})

    @action(methods=['get'], detail=True)
    def items(self, request: Request, pk=None):
        meal = get_object_or_404(MealSelection, pk=pk)
        profile = StudentProfile.objects.get(user=request.user)

        from random import choices
        options = {
            ItemType.PROTEIN: choices(meal.items.all(), k=3),
            ItemType.VEGETABLE: choices(meal.items.all(), k=3),
            ItemType.CARBOHYDRATE: choices(meal.items.all(), k=3)
        }

        # Build actual result (divvying up plates correctly)
        def to_pk(item_list):
            return list(map(lambda x: x.pk, item_list))

        result_choices = {}
        large_choice = LARGE_PORTION[profile.health_goal]
        result_choices['large'] = {
            'category': large_choice,
            'items': to_pk(options.pop(large_choice))
        }
        for plate_section, (category, items) in zip(('small1', 'small2'), options.items()):
            result_choices[plate_section] = {
                'category': category,
                'items': to_pk(items)
            }

        return Response(result_choices)

    @action(methods=['get'], detail=False)
    def portions(self, request: Request):
        req_ser = PortionRequestSerializer(data=request.query_params)
        req_ser.is_valid(raise_exception=True)
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
