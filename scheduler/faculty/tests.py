from django.test import TestCase
from django.urls import reverse
from scheduler.organization.models import Organization
from scheduler.models import DateTimeSlot
from scheduler.faculty.models import Faculty

class FacultyViewsTest(TestCase):
    def setUp(self):
        # Create an organization with 2 days, 3 slots/day
        self.org = Organization.objects.create(
            name="Test Org", days_per_week=2, slots_per_day=3
        )
        # Create the DateTimeSlots for this org
        slots = [
            DateTimeSlot(organization=self.org, day=d, time=t)
            for d in range(1, self.org.days_per_week + 1)
            for t in range(1, self.org.slots_per_day + 1)
        ]
        DateTimeSlot.objects.bulk_create(slots)
        # Pick two slots for testing M2M
        self.slot1 = DateTimeSlot.objects.first()
        self.slot2 = DateTimeSlot.objects.last()
        # Create an existing faculty
        self.fac = Faculty.objects.create(
            organization=self.org,
            faculty_id="F001",
            name="Alice",
            priority=5,
        )
        self.fac.slot_choices.set([self.slot1, self.slot2])

    def test_list_view_filters_by_org(self):
        # Create another org and a faculty under it
        other = Organization.objects.create(name="Other", days_per_week=1, slots_per_day=1)
        Faculty.objects.create(organization=other, faculty_id="X", name="Bob", priority=1)

        url = reverse('faculty_list', kwargs={'org_id': self.org.id})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        qs = resp.context['faculty_list']
        self.assertIn(self.fac, qs)
        # Bob should not appear
        self.assertNotIn(Faculty.objects.get(name="Bob"), qs)
        # org in context
        self.assertEqual(resp.context['organization'], self.org)

    def test_create_view_get(self):
        url = reverse('faculty_create', kwargs={'org_id': self.org.id})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'name="faculty_id"')
        self.assertContains(resp, 'name="slot_choices"')

    def test_create_view_post(self):
        url = reverse('faculty_create', kwargs={'org_id': self.org.id})
        data = {
            'faculty_id': 'F002',
            'name': 'Charlie',
            'priority': 3,
            'slot_choices': [self.slot1.id, self.slot2.id],
        }
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 302)
        new = Faculty.objects.get(faculty_id='F002')
        # simpler list compare instead of assertQuerysetEqual
        self.assertEqual(
            list(new.slot_choices.order_by('id')),
            [self.slot1, self.slot2]
        )

    def test_detail_view(self):
        url = reverse('faculty_detail', kwargs={'pk': self.fac.pk, 'org_id': self.org.id})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        # object in context
        self.assertEqual(resp.context['faculty'], self.fac)
        # org in context
        self.assertEqual(resp.context['organization'], self.org)
        # should list chosen slots
        self.assertContains(resp, f"Day:{self.slot1.day} Time:{self.slot1.time}")

    def test_update_view_get(self):
        url = reverse('faculty_update', kwargs={'pk': self.fac.pk, 'org_id': self.org.id})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        # look for value="39" followed by selected
        self.assertContains(resp, f'value="{self.slot1.id}" selected')
    def test_update_view_post(self):
        url = reverse('faculty_update', kwargs={'pk': self.fac.pk, 'org_id': self.org.id})
        data = {
            'faculty_id': 'F001',
            'name': 'Alice Updated',
            'priority': 9,
            'slot_choices': [self.slot1.id],
        }
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 302)
        self.fac.refresh_from_db()
        self.assertEqual(self.fac.name, 'Alice Updated')
        self.assertEqual(list(self.fac.slot_choices.all()), [self.slot1])

    def test_delete_view(self):
        url = reverse('faculty_delete', kwargs={'pk': self.fac.pk, 'org_id': self.org.id})
        # GET confirms deletion
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        # POST actually deletes
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        with self.assertRaises(Faculty.DoesNotExist):
            Faculty.objects.get(pk=self.fac.pk)
