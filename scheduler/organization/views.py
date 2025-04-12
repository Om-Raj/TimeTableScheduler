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
