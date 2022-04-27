import datetime

from django.shortcuts import get_object_or_404
from rest_framework import viewsets, serializers
from rest_framework.response import Response

from backend.models import ImageQueueEntry, StudentProfile, MealItem


class ImageQueueEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageQueueEntry
        exclude = ('timestamp', 'profile')


class ItemImageViewSet(viewsets.ViewSet):
    def create(self, request):
        ser = ImageQueueEntrySerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        entry = ImageQueueEntry(**ser.validated_data,
                                timestamp=datetime.datetime.utcnow(),
                                profile=StudentProfile.objects.get(user=request.user))
        entry.save()

        return Response(f'Added image to queue.  Queue now has {ImageQueueEntry.objects.count()} images.')

    def retrieve(self, request, pk=None):
        item: MealItem = get_object_or_404(MealItem, pk=pk)
        return Response({'url': item.image.url if item.image else None})
