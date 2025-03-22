from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from scheduler.models import DateTimeSlot
from scheduler.organization.models import Organization
from scheduler.room.models import Room
from scheduler.faculty.models import Faculty
from scheduler.course.models import Course
from scheduler.group.models import Group


class TimeTable(models.Model):
    organization = models.ForeignKey(to=Organization, on_delete=models.CASCADE)
    year = models.PositiveSmallIntegerField(validators=(
        MinValueValidator(limit_value=1900, message='Year cannot be less than 1900'),
        MinValueValidator(limit_value=2100, message='Year cannot be more than 2100'),
    ))
    semester = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_created=True)


class Slot(models.Model):
    time_table = models.ForeignKey(to=TimeTable, on_delete=models.CASCADE)
    date_time_slot = models.ForeignKey(to=DateTimeSlot, null=True, on_delete=models.SET_NULL)
    duration = models.PositiveSmallIntegerField(blank=True, default=1)
    room = models.ForeignKey(to=Room, null=True, on_delete=models.SET_NULL)
    faculty = models.ForeignKey(to=Faculty, null=True, on_delete=models.SET_NULL)
    course = models.ForeignKey(to=Course, on_delete=models.CASCADE)
    group = models.ForeignKey(to=Group, on_delete=models.CASCADE)
