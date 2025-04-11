from django.test import TestCase
from django.db import IntegrityError

from scheduler.organization.models import Organization
from scheduler.course.models import Course
from scheduler.room.models import Room

class CourseModelTests(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="Test Org", days_per_week=5, slots_per_day=8)
        self.room = Room.objects.create(organization=self.org, room_id="R1", capacity=30)

    def test_create_course(self):
        """Test creating a Course and adding rooms."""
        course = Course.objects.create(organization=self.org, course_id="C1", title="Math")
        course.rooms.add(self.room)
        self.assertEqual(course.course_id, "C1")
        self.assertEqual(course.title, "Math")
        self.assertEqual(str(course), "Test Org - Math")
        self.assertIn(self.room, course.rooms.all())

    def test_unique_course_id_per_organization(self):
        """Test that course_id is unique per organization."""
        Course.objects.create(organization=self.org, course_id="C1", title="Math")
        with self.assertRaises(IntegrityError):
            Course.objects.create(organization=self.org, course_id="C1", title="Science")