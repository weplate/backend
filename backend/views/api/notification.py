from django.urls import include, path
from django.utils import timezone
from rest_framework import viewsets, serializers, mixins
from rest_framework.routers import DefaultRouter

from backend.models.token import ExpoPushToken


class ExpoPushTokenWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpoPushToken
        fields = '__all__'

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    timestamp = serializers.HiddenField(default=timezone.now)


class ExpoPushTokenReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpoPushToken
        exclude = ['user']


class ExpoPushTokenViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    def get_queryset(self):
        return ExpoPushToken.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        return ExpoPushTokenReadSerializer if self.action == 'list' else ExpoPushTokenWriteSerializer


router = DefaultRouter()

router.register(r'expo_push_token', ExpoPushTokenViewSet, basename='ExpoPushTokenViewSet')

urlpatterns = [
    path('', include(router.urls))
]
