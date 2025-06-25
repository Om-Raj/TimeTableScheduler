from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404

from .models import Faculty
from scheduler.organization.models import Organization
from scheduler.models import DateTimeSlot
from scheduler.mixins import OrganizationContextMixin


class FacultyListView(OrganizationContextMixin, ListView):
    model = Faculty
    template_name = 'scheduler/faculty/list.html'

    def get_queryset(self):
        return Faculty.objects.filter(organization__id=self.kwargs['org_id'])


class FacultyCreateView(OrganizationContextMixin, CreateView):
    model = Faculty
    template_name = 'scheduler/faculty/create.html'
    fields = ('faculty_id', 'name', 'priority', 'slot_choices')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['slot_choices'].queryset = DateTimeSlot.objects.filter(
            organization__id=self.kwargs['org_id']
        )
        return form

    def form_valid(self, form):
        form.instance.organization = get_object_or_404(Organization, id=self.kwargs['org_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('faculty_detail', kwargs={
            'pk': self.object.pk,
            'org_id': self.object.organization.id
        })


class FacultyDetailView(OrganizationContextMixin, DetailView):
    model = Faculty
    template_name = 'scheduler/faculty/detail.html'

    def get_queryset(self):
        return super().get_queryset().filter(organization_id=self.kwargs['org_id'])


class FacultyDeleteView(OrganizationContextMixin, DeleteView):
    model = Faculty
    template_name = 'scheduler/faculty/delete.html'

    def get_queryset(self):
        return super().get_queryset().filter(organization_id=self.kwargs['org_id'])

    def get_success_url(self):
        return reverse_lazy('faculty_list', kwargs={'org_id': self.kwargs['org_id']})


class FacultyUpdateView(OrganizationContextMixin, UpdateView):
    model = Faculty
    template_name = 'scheduler/faculty/update.html'
    fields = ('name', 'priority', 'slot_choices')

    def get_queryset(self):
        return super().get_queryset().filter(organization_id=self.kwargs['org_id'])

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['slot_choices'].queryset = DateTimeSlot.objects.filter(
            organization__id=self.kwargs['org_id']
        )
        return form

    def get_success_url(self):
        return reverse('faculty_detail', kwargs={
            'pk': self.object.pk,
            'org_id': self.kwargs['org_id']
        })
