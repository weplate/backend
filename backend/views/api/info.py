import datetime

from django.shortcuts import get_object_or_404
from rest_framework import viewsets, serializers
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.models import School, StudentProfile, Ingredient, MealSelection, MealItem
from backend.utils import IsStudent

MAX_MEALS = 5


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = '__all__'


class SchoolViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = []

    queryset = School.objects.all()
    serializer_class = SchoolSerializer


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientViewSet(viewsets.ViewSet):
    permission_classes = []

    def list(self, _):
        return Response({'detail': 'please query ingredients/<school_id>'})

    def retrieve(self, _, pk=None):
        return Response(IngredientSerializer(Ingredient.objects.filter(school__id=pk), many=True).data)


class ReadMealItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealItem
        exclude = ['school']


class MealSelectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealSelection
        fields = '__all__'


class DetailMealSelectionSerializer(MealSelectionSerializer):
    items = ReadMealItemSerializer(many=True)


class MealSelectionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MealSelectionSerializer

    def get_queryset(self):
        profile = StudentProfile.objects.get(user=self.request.user)

        objects = MealSelection.objects.filter(school=profile.school).order_by('timestamp')
        if 'group' in self.request.query_params:
            objects = objects.filter(group=self.request.query_params['group'])
        if 'date' in self.request.query_params:
            dt = datetime.date.fromisoformat(self.request.query_params['date'])
            objects = objects.filter(timestamp__year=dt.year, timestamp__month=dt.month, timestamp__day=dt.day)

        return objects[:MAX_MEALS]

    def retrieve(self, request, pk=None, *args, **kwargs):
        meal = get_object_or_404(MealSelection, pk=pk)
        return Response(DetailMealSelectionSerializer(meal).data)


class SchoolMealItemsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ReadMealItemSerializer

    def get_queryset(self):
        profile = StudentProfile.objects.get(user=self.request.user)
        return MealItem.objects.filter(school=profile.school)
