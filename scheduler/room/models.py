from django.db import models

from scheduler.organization.models import Organization


class Room(models.Model):
    organization = models.ForeignKey(to=Organization, on_delete=models.CASCADE)
    room_id = models.CharField(max_length=10, primary_key=True)
    is_lab = models.BooleanField(blank=True, default=False)
    capacity = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ('organization', 'room_id')