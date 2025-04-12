from django.db import models
from scheduler.organization.models import Organization

class DateTimeSlot(models.Model):
    organization = models.ForeignKey(to=Organization, on_delete=models.CASCADE)
    day = models.PositiveSmallIntegerField()
    time = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = (('organization', 'day', 'time'),)

    def __str__(self):
        return f"Day:{self.day} Time:{self.time}"

