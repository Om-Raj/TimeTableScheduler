# scheduler/organization/views.py

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse, reverse_lazy

from .models import Organization
from scheduler.models import DateTimeSlot  

class OrganizationListView(ListView):
    model = Organization
    template_name = 'scheduler/organization/list.html'


class OrganizationCreateView(CreateView):
    model = Organization
    template_name = 'scheduler/organization/create.html'
    fields = ('name', 'days_per_week', 'slots_per_day')

    def form_valid(self, form):
        # First save the Organization so self.object is set
        response = super().form_valid(form)
        org = self.object

        # Build all the slots in memory
        slots = [
            DateTimeSlot(organization=org, day=day, time=slot)
            for day in range(1, org.days_per_week + 1)
            for slot in range(1, org.slots_per_day + 1)
        ]
        # Bulk‐insert them in one query
        DateTimeSlot.objects.bulk_create(slots)

        return response

    def get_success_url(self):
        return reverse('org_detail', kwargs={'org_id': self.object.id})


class OrganizationDetailView(DetailView):
    model = Organization
    pk_url_kwarg = 'org_id'
    template_name = 'scheduler/organization/detail.html'


class OrganizationDeleteView(DeleteView):
    model = Organization
    pk_url_kwarg = 'org_id'
    template_name = 'scheduler/organization/delete.html'
    success_url = reverse_lazy('org_list')


class OrganizationUpdateView(UpdateView):
    model = Organization
    pk_url_kwarg = 'org_id'
    template_name = 'scheduler/organization/update.html'
    fields = ('name', 'days_per_week', 'slots_per_day')

    def get_success_url(self):
        return reverse('org_detail', kwargs={'org_id': self.object.id})
