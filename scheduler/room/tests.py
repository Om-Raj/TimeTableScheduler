from django.test import TestCase, Client
from django.urls import reverse
from django.db import IntegrityError
from scheduler.organization.models import Organization
from scheduler.room.models import Room

class RoomModelTest(TestCase):
    def setUp(self):
        # Create an Organization instance required by Room.
        self.organization = Organization.objects.create(
            name="IIT JSR",
            days_per_week=5,
            slots_per_day=6
        )
        # Create an initial Room instance.
        self.room = Room.objects.create(
            organization=self.organization,
            room_id="LABCS001",
            is_lab=True,
            capacity=40
        )

    def test_room_creation(self):
        """Test that a Room instance is created with the correct attributes."""
        self.assertEqual(self.room.room_id, "LABCS001")
        self.assertTrue(self.room.is_lab)
        self.assertEqual(self.room.capacity, 40)
        self.assertEqual(self.room.organization.name, "IIT JSR")

    def test_room_str_method(self):
        """Test the __str__ method returns the expected string."""
        expected_str = "IIT JSR - room_id:LABCS001"
        self.assertEqual(str(self.room), expected_str)

    def test_unique_room_constraint(self):
        """Test that creating a duplicate Room (same room_id within an organization)
        raises an IntegrityError.
        """
        with self.assertRaises(IntegrityError):
            Room.objects.create(
                organization=self.organization,
                room_id="LABCS001",  # duplicate room_id
                is_lab=False,
                capacity=30
            )


class RoomViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Create the organization required for room views.
        self.organization = Organization.objects.create(
            name="IIT JSR",
            days_per_week=5,
            slots_per_day=6
        )
        # Create a Room instance.
        self.room = Room.objects.create(
            organization=self.organization,
            room_id="LABCS002",
            is_lab=False,
            capacity=50
        )

    def test_room_list_view(self):
        """
        Ensure that the RoomListView correctly lists rooms for a given organization.
        """
        url = reverse('room_list', kwargs={'org_id': self.organization.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Check that the room's room_id appears in the response content.
        self.assertContains(response, self.room.room_id)

    def test_room_detail_view(self):
        """
        Ensure that the RoomDetailView displays the details of a room.
        """
        url = reverse('room_detail', kwargs={
            'org_id': self.organization.id,
            'room_id': self.room.room_id,
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Verify that the room details are visible in the output.
        self.assertContains(response, self.room.room_id)
        self.assertContains(response, str(self.room.capacity))

    def test_room_create_view_post(self):
        """
        Test that a new Room is created via the RoomCreateView.
        """
        url = reverse('room_create', kwargs={'org_id': self.organization.id})
        data = {
            'room_id': 'LABCS003',
            'is_lab': True,
            'capacity': 35,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Expecting a redirect after creation.
        # Verify the new room was created.
        new_room = Room.objects.get(room_id='LABCS003')
        self.assertEqual(new_room.capacity, 35)

    def test_room_update_view_post(self):
        """
        Test that updating a room via RoomUpdateView works correctly.
        """
        url = reverse('room_update', kwargs={
            'org_id': self.organization.id,
            'room_id': self.room.room_id,
        })
        data = {
            'room_id': self.room.room_id,  # typically remains unchanged
            'is_lab': True,  # update the value if needed
            'capacity': 55,  # new capacity
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.room.refresh_from_db()
        self.assertEqual(self.room.capacity, 55)

    def test_room_delete_view_post(self):
        """
        Test that a POST to RoomDeleteView deletes the room.
        """
        url = reverse('room_delete', kwargs={
            'org_id': self.organization.id,
            'room_id': self.room.room_id,
        })
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        with self.assertRaises(Room.DoesNotExist):
            Room.objects.get(room_id=self.room.room_id)
