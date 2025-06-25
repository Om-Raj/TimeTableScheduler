from django.db import models
from django.conf import settings


class Organization(models.Model):
    name = models.CharField(max_length=100, unique=True)
    # owner = models.ForeignKey(
    #     settings.AUTH_USER_MODEL,
    #     on_delete=models.CASCADE,
    # )
    days_per_week = models.PositiveSmallIntegerField(default=5)
    slots_per_day = models.PositiveSmallIntegerField(default=8)

    def __str__(self):
        return self.name