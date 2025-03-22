from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse, reverse_lazy
from django.http import Http404

from .models import TimeTable
from scheduler.organization.models import Organization


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

    def get_object(self, queryset = None):
        return get_timetable_object(self, queryset=queryset)


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