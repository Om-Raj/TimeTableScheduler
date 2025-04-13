from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, FormView
from django.urls import reverse, reverse_lazy
from django.http import Http404
from django.shortcuts import render, get_object_or_404

from scheduler.organization.models import Organization
from scheduler.room.models import Room
from scheduler.algorithm.scheduler import Scheduler

from .models import TimeTable, Section
from .forms import RunSchedulerForm

# helper function to get timetable object
def get_timetable_object(self, queryset = None):
    if queryset is None:
        queryset = self.get_queryset()
    org_id = self.kwargs['org_id']
    timetable_id = self.kwargs['timetable_id']
    try:
        return queryset.get(organization__id=org_id, timetable_id=timetable_id)
    except:
        raise Http404('TimeTable not found')


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

class SectionCreateView(CreateView):
    model = Section
    fields = ('faculty', 'course', 'group', 'duration')
    template_name = 'scheduler/section/create.html'

    def form_valid(self, form):
        timetable_id = self.kwargs['timetable_id']
        timetable = get_object_or_404(TimeTable, timetable_id=timetable_id)
        form.instance.timetable = timetable
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('timetable_detail', kwargs={'org_id': self.kwargs['org_id'], 'timetable_id': self.kwargs['timetable_id']})
    
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

    def get_object(self, queryset = None):
        return get_timetable_object(self, queryset=queryset)

    def get_context_data(self, **kwargs):
        """Add slots related to this timetable to the context."""
        context = super().get_context_data(**kwargs)
        context['sections'] = Section.objects.filter(timetable=self.object)
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

    def get_object(self, queryset = None):
        return get_timetable_object(self, queryset=queryset)

    def get_success_url(self):
        return get_timetable_success_url(self)


class TimetableScheduleView(FormView):
    form_class = RunSchedulerForm
    template_name = 'scheduler/timetable/schedule.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['timetable'] = get_timetable_object(self, queryset=TimeTable.objects.all())
        return context

    def form_valid(self, form):
        org_id = self.kwargs['org_id']
        timetable_id = self.kwargs['timetable_id']
        timetable = get_timetable_object(self, queryset=TimeTable.objects.all())
        scheduler = Scheduler(org_id=org_id, timetable_id=timetable_id)
        scheduler.run()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('timetable_detail', kwargs={'org_id': self.kwargs['org_id'], 'timetable_id': self.kwargs['timetable_id']})