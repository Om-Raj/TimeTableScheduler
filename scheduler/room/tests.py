from django.test import TestCase

from scheduler.organization.models import Organization
from scheduler.room.models import Room
from django.db import IntegrityError

class RoomModelTests(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="Test Org", days_per_week=5, slots_per_day=8)

    def test_create_room(self):
        """Test creating a Room with valid data."""
        room = Room.objects.create(organization=self.org, room_id="R1", capacity=30)
        self.assertEqual(room.room_id, "R1")
        self.assertFalse(room.is_lab)  # Default value
        self.assertEqual(room.capacity, 30)
        self.assertEqual(str(room), "Test Org - room_id:R1")

    def test_unique_room_id_per_organization(self):
        """Test that room_id is unique per organization."""
        Room.objects.create(organization=self.org, room_id="R1", capacity=30)
        with self.assertRaises(IntegrityError):
            Room.objects.create(organization=self.org, room_id="R1", capacity=40)