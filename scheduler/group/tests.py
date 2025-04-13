from django.test import TestCase, Client
from django.urls import reverse
from scheduler.organization.models import Organization
from scheduler.group.models import Group

class GroupViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Create an Organization since Group is linked to an organization.
        self.organization = Organization.objects.create(
            name="Test Organization",
            days_per_week=5,
            slots_per_day=8
        )
        # Create a sample Group.
        self.group = Group.objects.create(
            organization=self.organization,
            group_id="G001",
            size=30
        )

    def test_group_list_view(self):
        """
        Test that the GroupListView displays groups for an organization.
        """
        url = reverse('group_list', kwargs={'org_id': self.organization.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Verify the group identifier appears in the response.
        self.assertContains(response, self.group.group_id)

    def test_group_detail_view(self):
        """
        Test that the GroupDetailView returns the correct group details.
        """
        url = reverse('group_detail', kwargs={
            'org_id': self.organization.id,
            'group_id': self.group.group_id,
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Check that the group_id and size are rendered.
        self.assertContains(response, self.group.group_id)
        self.assertContains(response, str(self.group.size))

    def test_group_create_view_get(self):
        """
        Test that the GET request to GroupCreateView loads the creation form.
        """
        url = reverse('group_create', kwargs={'org_id': self.organization.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Check that the form includes the group_id field label.
        self.assertContains(response, "group_id")

    def test_group_create_view_post(self):
        """
        Test that a valid POST to GroupCreateView creates a new group.
        """
        url = reverse('group_create', kwargs={'org_id': self.organization.id})
        data = {
            'group_id': 'G002',
            'size': 25,
        }
        response = self.client.post(url, data)
        # Expect a redirect after successful creation.
        self.assertEqual(response.status_code, 302)
        new_group = Group.objects.get(group_id='G002')
        self.assertEqual(new_group.size, 25)
        self.assertEqual(new_group.organization, self.organization)

    def test_group_update_view_get(self):
        """
        Test that the GET request to GroupUpdateView loads the update form.
        """
        url = reverse('group_update', kwargs={
            'org_id': self.organization.id,
            'group_id': self.group.group_id,
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Verify that the existing group information is displayed.
        self.assertContains(response, self.group.group_id)

    def test_group_update_view_post(self):
        """
        Test that submitting new data to GroupUpdateView updates the group.
        """
        url = reverse('group_update', kwargs={
            'org_id': self.organization.id,
            'group_id': self.group.group_id,
        })
        data = {
            'group_id': self.group.group_id,  # Typically remains unchanged.
            'size': 35,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        # Refresh from the database to check if the update persisted.
        self.group.refresh_from_db()
        self.assertEqual(self.group.size, 35)

    def test_group_delete_view_post(self):
        """
        Test that a POST request to GroupDeleteView deletes the group.
        """
        url = reverse('group_delete', kwargs={
            'org_id': self.organization.id,
            'group_id': self.group.group_id,
        })
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        with self.assertRaises(Group.DoesNotExist):
            Group.objects.get(group_id=self.group.group_id)
