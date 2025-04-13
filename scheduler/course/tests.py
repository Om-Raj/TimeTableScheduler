from django.test import TestCase, Client
from django.urls import reverse
from scheduler.organization.models import Organization
from scheduler.room.models import Room
from scheduler.course.models import Course

class CourseViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create an Organization. Note that Organization requires
        # name, days_per_week, and slots_per_day.
        self.organization = Organization.objects.create(
            name="Test Organization",
            days_per_week=5,
            slots_per_day=8
        )

        # Create a Room associated with the Organization.
        # Room model uses room_id as a primary key.
        self.room = Room.objects.create(
            organization=self.organization,
            room_id="R101",
            is_lab=False,
            capacity=40
        )

        # Create a Course linked to the Organization.
        # The Course model uses course_id as primary key.
        self.course = Course.objects.create(
            organization=self.organization,
            course_id="CS101",
            title="Introduction to Computer Science"
        )
        # Associate the Room with the Course (ManyToManyField).
        self.course.rooms.add(self.room)

    def test_course_list_view(self):
        """
        Verify that the CourseListView for an organization displays the course.
        """
        url = reverse('course_list', kwargs={'org_id': self.organization.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.course.course_id)

    def test_course_detail_view(self):
        """
        Verify that CourseDetailView returns the correct details for a Course.
        """
        url = reverse('course_detail', kwargs={
            'org_id': self.organization.id,
            'course_id': self.course.course_id,
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.course.title)
        # Check that the associated Room's room_id appears as well.
        self.assertContains(response, self.room.room_id)

    def test_course_create_view_get(self):
        """
        Verify that the GET request to CourseCreateView loads the creation form.
        """
        url = reverse('course_create', kwargs={'org_id': self.organization.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Example check: The form should include the field label "course_id"
        self.assertContains(response, "course_id")

    def test_course_create_view_post(self):
        """
        Verify that a valid POST request to CourseCreateView creates a Course.
        """
        url = reverse('course_create', kwargs={'org_id': self.organization.id})
        data = {
            'course_id': 'CS102',
            'title': 'Data Structures',
            # If the form expects room selections as list of primary keys.
            'rooms': [self.room.room_id],
        }
        response = self.client.post(url, data)
        # On success, the view usually redirects.
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Course.objects.filter(course_id='CS102').exists())

    def test_course_update_view_get(self):
        """
        Verify that the GET request to CourseUpdateView shows the form with existing data.
        """
        url = reverse('course_update', kwargs={
            'org_id': self.organization.id,
            'course_id': self.course.course_id,
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.course.title)

    def test_course_update_view_post(self):
        """
        Verify that posting updated data to CourseUpdateView properly updates a Course.
        """
        url = reverse('course_update', kwargs={
            'org_id': self.organization.id,
            'course_id': self.course.course_id,
        })
        data = {
            'course_id': self.course.course_id,  # course_id generally remains unchanged.
            'title': 'Updated Course Title',
            # Keep the same room assignment (if required by the form).
            'rooms': [self.room.room_id],
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        # Refresh from DB to verify the changes.
        self.course.refresh_from_db()
        self.assertEqual(self.course.title, 'Updated Course Title')

    def test_course_delete_view_post(self):
        """
        Verify that a POST request to CourseDeleteView deletes the Course.
        """
        url = reverse('course_delete', kwargs={
            'org_id': self.organization.id,
            'course_id': self.course.course_id,
        })
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        with self.assertRaises(Course.DoesNotExist):
            Course.objects.get(course_id=self.course.course_id)
