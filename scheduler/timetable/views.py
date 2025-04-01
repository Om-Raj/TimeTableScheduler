from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse, reverse_lazy
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from .models import TimeTable,Slot
from scheduler.organization.models import Organization
from scheduler.room.models import Room

# helper function to get timetable object
def get_timetable_object(self, queryset = None):
    if queryset is None:
        queryset = self.get_queryset()
    org_id = self.kwargs['org_id']
    timetable_id = self.kwargs['timetable_id']
    try:
        return queryset.get(organization__id=org_id, timetable_id=timetable_id)
    except:
        return Http404('TimeTable not found')


# helper function to get success url
def get_timetable_success_url(self):
    return reverse('timetable_detail', kwargs={
        'org_id': self.object.organization.id,
        'timetable_id': self.object.timetable_id,
    })


class TimeTableListView(ListView):
    model = TimeTable
    template_name = 'scheduler/timetable/list.html'

    def get_queryset(self):
        """Filter timetables by organization ID from the URL."""
        org_id = self.kwargs.get('org_id') 
        #this is organization _, _ id
        return TimeTable.objects.filter(organization__id=org_id)

class SlotCreateView(CreateView):
    model = Slot
    fields=('date_time_slot', 'duration', 'room', 'faculty', 'course', 'group')
    template_name = 'scheduler/slot/create.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filter the room field queryset to only show rooms with the current org_id
        org_id = self.kwargs.get('org_id')
        form.fields['room'].queryset = Room.objects.filter(organization__id=org_id)
        form.fields['faculty'].queryset = form.fields['faculty'].queryset.filter(organization__id=org_id)
        form.fields['group'].queryset = form.fields['group'].queryset.filter(organization__id=org_id)
        form.fields['course'].queryset = form.fields['course'].queryset.filter(organization__id=org_id)
        return form

    def form_valid(self, form):
        timetable_id = self.kwargs['timetable_id']
        form.instance.time_table = get_object_or_404(TimeTable, id=timetable_id)
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect to the timetable detail view after successful form submission"""
        return reverse_lazy('timetable_detail', kwargs={'org_id': self.kwargs['org_id'], 'pk': self.kwargs['timetable_id']})

    
    def get_context_data(self, **kwargs):
        """Pass organization ID and timetable ID to the template context"""
        context = super().get_context_data(**kwargs)
        context['org_id'] = self.kwargs['org_id']
        context['timetable_id'] = self.kwargs['timetable_id']
        return context

class TimeTableCreateView(CreateView):
    model = TimeTable
    template_name = 'scheduler/timetable/create.html'
    fields = ('year', 'semester')

    def get_success_url(self):
        return get_timetable_success_url(self)

    def form_valid(self, form):
        org_id = self.kwargs['org_id']
        form.instance.organization = Organization.objects.get(id=org_id)
        return super().form_valid(form)
    


class TimeTableDetailView(DetailView):
    model = TimeTable
    template_name = 'scheduler/timetable/detail.html'
    context_object_name = 'timetable'
    
    def get_context_data(self, **kwargs):
        """Add slots related to this timetable to the context."""
        context = super().get_context_data(**kwargs)
        context['slots'] = Slot.objects.filter(time_table=self.object) 
        return context


class TimeTableDeleteView(DeleteView):
    model = TimeTable
    template_name = 'scheduler/timetable/delete.html'
    success_url = reverse_lazy('timetable_list')

    def get_object(self, queryset = None):
        return get_timetable_object(self, queryset=queryset)



class TimeTableUpdateView(UpdateView):
    model = TimeTable
    template_name = 'scheduler/timetable/update.html'
    fields = ('year', 'semester')

    def get_success_url(self):
        return get_timetable_success_url(self)