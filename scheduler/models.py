from django.db import models


class DateTimeSlot(models.Model):
    day = models.PositiveSmallIntegerField()
    time = models.PositiveSmallIntegerField()

