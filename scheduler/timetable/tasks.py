from celery import shared_task
from website.settings import ALGO_TIME_LIMIT
from scheduler.algorithm.scheduler import Scheduler
from .models import TimeTable, ScheduleStatus

@shared_task(bind=True)
def run_scheduler_task(self, org_id, timetable_id, time_limit):
    try:
        timetable = TimeTable.objects.get(timetable_id=timetable_id, organization__id=org_id)
        status, _ = ScheduleStatus.objects.get_or_create(timetable=timetable)
        status.status = "RUNNING"
        status.task_id = self.request.id
        status.save()

        time_limit = min(time_limit, ALGO_TIME_LIMIT)
        scheduler = Scheduler(org_id=org_id, timetable_id=timetable_id, time_limit=time_limit)
        scheduler.run()

        status.status = "SUCCESS"
        status.save()
    except Exception as e:
        status.status = "FAILURE"
        status.save()
        raise