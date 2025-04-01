from django.db import models

from scheduler.organization.models import Organization


class Group(models.Model):
    organization = models.ForeignKey(to=Organization, on_delete=models.CASCADE)
    group_id = models.CharField(max_length=50)
    size = models.PositiveSmallIntegerField()
    
    class Meta:
        unique_together = ('organization', 'group_id')

    def __str__(self):
        return f"{self.organization.name} - {self.group_id}"