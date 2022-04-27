from django.db import models

from . import StudentProfile
from .meal import MealItem

IMAGE_QUEUE_DIR = 'image_queue_image'


class ImageQueueEntry(models.Model):
    image = models.ImageField(upload_to=IMAGE_QUEUE_DIR)
    item = models.ForeignKey(to=MealItem, on_delete=models.CASCADE)
    profile = models.ForeignKey(to=StudentProfile, on_delete=models.SET_NULL, blank=True, null=True)
    timestamp = models.DateTimeField()
