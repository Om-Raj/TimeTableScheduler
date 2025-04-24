from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404

from .models import Faculty
from scheduler.organization.models import Organization  
from scheduler.models import DateTimeSlot

class FacultyListView(ListView):
    model = Faculty
    template_name = 'scheduler/faculty/list.html'

    def get_queryset(self):
        # Retrieve the current organization from the URL
        self.organization = get_object_or_404(Organization, id=self.kwargs.get('org_id'))
        # Return only faculties for this organization
        return Faculty.objects.filter(organization=self.organization)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass the organization to the template context
        context['organization'] = self.organization
        return context


class FacultyCreateView(CreateView):
    model = Faculty
    template_name = 'scheduler/faculty/create.html'
    fields = ('faculty_id', 'name', 'priority', 'slot_choices')

    def get_organization(self):
        return get_object_or_404(Organization, id=self.kwargs['org_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add the current organization to the context
        context['organization'] = get_object_or_404(Organization, id=self.kwargs.get('org_id'))
        return context
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        org = self.get_organization()
        form.fields['slot_choices'].queryset = DateTimeSlot.objects.filter(
            organization=org
        )
        return form

    def form_valid(self, form):
        form.instance.organization = self.get_organization()
        return super().form_valid(form)

    def get_success_url(self):
        # Redirect to the detail view, passing both faculty id and organization id
        return reverse('faculty_detail', kwargs={
            'pk': self.object.pk,
            'org_id': self.object.organization.id
        })


class FacultyDetailView(DetailView):
    model = Faculty
    template_name = 'scheduler/faculty/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ensure the current organization is available in context
        context['organization'] = get_object_or_404(Organization, id=self.kwargs.get('org_id'))
        return context


class FacultyDeleteView(DeleteView):
    model = Faculty
    template_name = 'scheduler/faculty/delete.html'

    def get_success_url(self):
        # After deletion, redirect back to the Faculty list for the current organization
        return reverse_lazy('faculty_list', kwargs={'org_id': self.kwargs.get('org_id')})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass the current organization to the template context
        context['organization'] = get_object_or_404(Organization, id=self.kwargs.get('org_id'))
        return context


class FacultyUpdateView(UpdateView):
    model = Faculty
    template_name = 'scheduler/faculty/update.html'
    fields = ('faculty_id', 'name', 'priority', 'slot_choices')

    def get_organization(self):
        return get_object_or_404(Organization, id=self.kwargs['org_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add the current organization to the context for use in the template
        context['organization'] = get_object_or_404(Organization, id=self.kwargs.get('org_id'))
        return context
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        org = self.get_organization()
        form.fields['slot_choices'].queryset = DateTimeSlot.objects.filter(
            organization=org
        )
        return form

    def get_success_url(self):
        # Redirect to the detail view after updating
        return reverse('faculty_detail', kwargs={
            'pk': self.object.pk,
            'org_id': self.kwargs.get('org_id')
        })
