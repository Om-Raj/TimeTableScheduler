from django.db import models

from scheduler.organization.models import Organization
from scheduler.room.models import Room


class Course(models.Model):
    organization = models.ForeignKey(to=Organization, on_delete=models.CASCADE)
    course_id = models.CharField(max_length=10, primary_key=True)
    title = models.CharField(max_length=255)

    # Require any of these rooms to be conducted
    rooms = models.ManyToManyField(to=Room, blank=True)

    # weekly_hours = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ('organization', 'course_id')

    def __str__(self):
        return f"{self.organization.name} - {self.title}"