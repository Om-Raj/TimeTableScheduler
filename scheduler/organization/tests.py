from django.test import TestCase
from django.core.exceptions import ValidationError
from scheduler.organization.models import Organization

class OrganizationModelTests(TestCase):
    def test_create_organization(self):
        """Test creating an Organization with valid data."""
        org = Organization.objects.create(name="Test Org", days_per_week=5, slots_per_day=8)
        self.assertEqual(org.name, "Test Org")
        self.assertEqual(org.days_per_week, 5)
        self.assertEqual(org.slots_per_day, 8)
        self.assertEqual(str(org), "Test Org")

    def test_invalid_days_per_week(self):
        """Test that days_per_week must be positive."""
        with self.assertRaises(ValidationError):
            org = Organization(name="Invalid Org", days_per_week=-1, slots_per_day=8)
            org.full_clean()  # Validate before saving