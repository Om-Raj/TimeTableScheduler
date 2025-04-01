from django.db import models

from scheduler.models import DateTimeSlot
from scheduler.organization.models import Organization


class Faculty(models.Model):
    organization = models.ForeignKey(to=Organization, on_delete=models.CASCADE)
    faculty_id = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    priority = models.SmallIntegerField()
    slot_choices = models.ManyToManyField(to=DateTimeSlot)

    class Meta:
        unique_together = ('organization', 'faculty_id')

    def __str__(self):
        return f"{self.organization.name} - {self.name}"
