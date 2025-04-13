from celery import shared_task

from scheduler.algorithm.scheduler import Scheduler
from .models import TimeTable, ScheduleStatus

@shared_task(bind=True)
def run_scheduler_task(self, org_id, timetable_id):
    try:
        timetable = TimeTable.objects.get(timetable_id=timetable_id, organization__id=org_id)
        status, _ = ScheduleStatus.objects.get_or_create(timetable=timetable)
        status.status = "RUNNING"
        status.task_id = self.request.id
        status.save()

        scheduler = Scheduler(org_id=org_id, timetable_id=timetable_id)
        scheduler.run()

        status.status = "SUCCESS"
        status.save()
    except Exception as e:
        status.status = "FAILURE"
        status.save()
        raise