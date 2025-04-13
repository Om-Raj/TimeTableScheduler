from django.test import TestCase
from django.urls import reverse

from scheduler.organization.models import Organization
from scheduler.models import DateTimeSlot

class OrganizationSlotGenerationTest(TestCase):
    def test_create_view_generates_slots(self):
        """
        Posting to OrganizationCreateView with days_per_week=3 and
        slots_per_day=4 should create exactly 12 DateTimeSlot objects
        for that organization, with the correct day/time values.
        """
        url = reverse('org_create')  # or whatever your URL name is
        data = {
            'name': 'Acme Corp',
            'days_per_week': 3,
            'slots_per_day': 4,
        }

        # Ensure no slots exist up‑front
        self.assertEqual(DateTimeSlot.objects.count(), 0)

        # Create the organization via the view
        resp = self.client.post(url, data)
        # Should redirect to detail
        self.assertEqual(resp.status_code, 302)

        # Fetch the new organization
        org = Organization.objects.get(name='Acme Corp')

        # Now there should be 3*4 = 12 slots
        slots = DateTimeSlot.objects.filter(organization=org)
        self.assertEqual(slots.count(), 12)

        # Spot‑check that some expected slots exist:
        self.assertTrue(
            slots.filter(day=1, time=1).exists(),
            "Expected a slot for day=1, time=1"
        )
        self.assertTrue(
            slots.filter(day=3, time=4).exists(),
            "Expected a slot for day=3, time=4"
        )

    def test_update_view_does_not_duplicate_slots(self):
        """
        If you later add an UpdateView that changes days_per_week or slots_per_day,
        you might want to ensure it doesn't re‑create slots.  For now we just
        assert that re‑posting the same create data doesn't double‑up.
        """
        url = reverse('org_create')
        data = {
            'name': 'Beta Inc',
            'days_per_week': 2,
            'slots_per_day': 2,
        }
        self.client.post(url, data)
        org = Organization.objects.get(name='Beta Inc')
        # first time: 4 slots
        self.assertEqual(DateTimeSlot.objects.filter(organization=org).count(), 4)

        # Post the same data again under a new org name to simulate duplication
        data2 = data.copy()
        data2['name'] = 'Beta Inc Clone'
        self.client.post(url, data2)
        clone = Organization.objects.get(name='Beta Inc Clone')
        self.assertEqual(DateTimeSlot.objects.filter(organization=clone).count(), 4)
        # original is untouched
        self.assertEqual(DateTimeSlot.objects.filter(organization=org).count(), 4)
