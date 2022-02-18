import datetime

from rest_framework import viewsets, serializers
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from backend.models import StudentProfile
from backend.views.common import IsStudent


MAX_LOG_ENTRIES = 20


def create_user_log_viewset(model_class):
    class LogModelSerializer(serializers.ModelSerializer):
        class Meta:
            model = model_class
            exclude = ['profile']

        timestamp = serializers.DateTimeField(read_only=True)

    class LogModelViewSet(viewsets.ReadOnlyModelViewSet):
        authentication_classes = [SessionAuthentication, TokenAuthentication]
        permission_classes = [IsAuthenticated, IsStudent]
        serializer_class = LogModelSerializer

        def get_queryset(self):
            return model_class.objects.filter(profile__user=self.request.user).order_by('-timestamp')[:MAX_LOG_ENTRIES]

        def create(self, request: Request):
            profile = StudentProfile.objects.get(user=request.user)
            ser = LogModelSerializer(data=request.data)
            ser.is_valid(raise_exception=True)
            cur_time = datetime.datetime.now()
            ser.save(profile=profile, timestamp=cur_time)

            return Response({'detail': f'saved meal choices at time {cur_time}'})

    return LogModelViewSet
