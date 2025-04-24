from django.test import TestCase, Client
from django.urls import reverse
from scheduler.organization.models import Organization
from scheduler.faculty.models import Faculty
from scheduler.course.models import Course
from scheduler.group.models import Group
from scheduler.room.models import Room
from scheduler.models import DateTimeSlot
from .models import TimeTable, Section, Slot

class TimeTableTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Create an Organization with the required days_per_week and slots_per_day.
        self.org = Organization.objects.create(
            name='Test University', 
            days_per_week=5, 
            slots_per_day=8
        )
        # Create related objects
        self.faculty = Faculty.objects.create(name='Dr. John Doe', organization=self.org)
        self.course = Course.objects.create(name='Algorithms', code='CS101', organization=self.org)
        self.group = Group.objects.create(name='Group A', organization=self.org)
        self.room = Room.objects.create(name='Room 101', organization=self.org)
        self.date_time_slot = DateTimeSlot.objects.create(day='Monday', start_time='09:00', end_time='10:00')

        # Create a TimeTable
        self.timetable = TimeTable.objects.create(
            organization=self.org,
            year=2024,
            semester='Fall',
            timetable_id='2024-Fall-0'
        )

    def test_create_timetable(self):
        self.assertEqual(TimeTable.objects.count(), 1)
        self.assertEqual(self.timetable.organization.name, 'Test University')

    def test_section_creation(self):
        section = Section.objects.create(
            timetable=self.timetable,
            faculty=self.faculty,
            course=self.course,
            group=self.group,
            duration=2
        )
        self.assertEqual(Section.objects.count(), 1)
        self.assertEqual(section.duration, 2)

    def test_slot_creation(self):
        section = Section.objects.create(
            timetable=self.timetable,
            faculty=self.faculty,
            course=self.course,
            group=self.group,
            duration=1
        )
        slot = Slot.objects.create(
            section=section,
            room=self.room,
            date_time_slot=self.date_time_slot
        )
        self.assertEqual(Slot.objects.count(), 1)
        self.assertEqual(slot.section, section)

    def test_timetable_list_view(self):
        url = reverse('timetable_list', kwargs={'org_id': self.org.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'scheduler/timetable/list.html')

    def test_timetable_detail_view(self):
        url = reverse('timetable_detail', kwargs={
            'org_id': self.org.id,
            'timetable_id': self.timetable.timetable_id
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'scheduler/timetable/detail.html')

    def test_timetable_create_view(self):
        url = reverse('timetable_create', kwargs={'org_id': self.org.id})
        data = {'year': 2025, 'semester': 'Spring'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Expect a redirect upon success
        self.assertEqual(TimeTable.objects.count(), 2)

    def test_timetable_update_view(self):
        url = reverse('timetable_update', kwargs={
            'org_id': self.org.id,
            'timetable_id': self.timetable.timetable_id
        })
        data = {'year': 2026, 'semester': 'Winter'}
        response = self.client.post(url, data)
        self.timetable.refresh_from_db()
        self.assertEqual(self.timetable.year, 2026)

    def test_timetable_delete_view(self):
        url = reverse('timetable_delete', kwargs={
            'org_id': self.org.id,
            'timetable_id': self.timetable.timetable_id
        })
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(TimeTable.objects.count(), 0)

    def test_add_section_view(self):
        url = reverse('section_create', kwargs={
            'org_id': self.org.id,
            'timetable_id': self.timetable.timetable_id
        })
        data = {
            'faculty': self.faculty.id,
            'course': self.course.id,
            'group': self.group.id,
            'duration': 1
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Section.objects.count(), 1)

    def test_schedule_form_view(self):
        url = reverse('timetable_schedule', kwargs={
            'org_id': self.org.id,
            'timetable_id': self.timetable.timetable_id
        })
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
