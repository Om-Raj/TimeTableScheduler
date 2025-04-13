from django.db import models


class DateTimeSlot(models.Model):
    day = models.PositiveSmallIntegerField()
    time = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"Day:{self.day} Time:{self.time}"

