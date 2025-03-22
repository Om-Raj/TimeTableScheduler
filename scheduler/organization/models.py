from django.db import models


class Organization(models.Model):
    name = models.CharField(max_length=255)
    days_per_week = models.PositiveSmallIntegerField()
    slots_per_day = models.PositiveSmallIntegerField()