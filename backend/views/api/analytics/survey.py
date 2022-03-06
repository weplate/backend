import datetime

from rest_framework import viewsets, serializers
from rest_framework.response import Response

from backend.models import LogTextFeedback


class TextFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogTextFeedback
        exclude = ['timestamp']


class TextFeedbackViewSet(viewsets.ViewSet):
    def list(self, _):
        return Response({'detail': 'Please POST this endpoint instead'})

    def create(self, request):
        ser = TextFeedbackSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        ser.save(timestamp=datetime.datetime.now())

        return Response({'detail': 'Ok'})