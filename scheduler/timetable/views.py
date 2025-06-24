from collections import defaultdict

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, FormView
from django.urls import reverse, reverse_lazy
from django.http import Http404
from django.shortcuts import get_object_or_404

from scheduler.organization.models import Organization
from scheduler.timetable.tasks import run_scheduler_task

from .models import TimeTable, Section, Slot, ScheduleStatus, Faculty, Group, Course
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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['organization'] = Organization.objects.get(id=self.kwargs['org_id'])
        return context

class SectionCreateView(CreateView):
    model = Section
    fields = ('faculty', 'course', 'group', 'duration')
    template_name = 'scheduler/section/create.html'

    def get_organization(self):
        return get_object_or_404(Organization, id=self.kwargs['org_id'])

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        org = self.get_organization()
        # Limit each dropdown to this org's items
        form.fields['faculty'].queryset = Faculty.objects.filter(organization=org)
        form.fields['course'].queryset  = Course.objects.filter(organization=org)
        form.fields['group'].queryset   = Group.objects.filter(organization=org)
        return form

    def form_valid(self, form):
        timetable = get_object_or_404(
            TimeTable,
            timetable_id=self.kwargs['timetable_id']
        )
        form.instance.timetable = timetable
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['org_id']       = self.kwargs['org_id']
        context['timetable_id'] = self.kwargs['timetable_id']
        return context

    def get_success_url(self):
        return reverse_lazy(
            'timetable_detail',
            kwargs={
                'org_id': self.kwargs['org_id'],
                'timetable_id': self.kwargs['timetable_id']
            }
        )

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
        """Add section and status of schedule related to this timetable to the context."""
        context = super().get_context_data(**kwargs)
        context['sections'] = Section.objects.filter(timetable=self.object)
        context['status'] = ScheduleStatus.objects.filter(timetable=self.object).first()
        return context


class TimeTableDeleteView(DeleteView):
    model = TimeTable
    template_name = 'scheduler/timetable/delete.html'

    def get_success_url(self):
        return reverse('timetable_list', kwargs={'org_id': self.kwargs['org_id']})

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


class TimeTableScheduleView(FormView):
    form_class = RunSchedulerForm
    template_name = 'scheduler/timetable/schedule.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['timetable'] = get_timetable_object(self, queryset=TimeTable.objects.all())
        return context

    def form_valid(self, form):
        org_id = self.kwargs['org_id']
        timetable_id = self.kwargs['timetable_id']
        task = run_scheduler_task.delay(org_id, timetable_id)

        # Store task ID and mark status
        timetable = TimeTable.objects.get(organization__id=org_id, timetable_id=timetable_id)
        status, _ = ScheduleStatus.objects.get_or_create(timetable=timetable)
        status.status = "PENDING"
        status.task_id = task.id
        status.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('timetable_detail', kwargs={'org_id': self.kwargs['org_id'], 'timetable_id': self.kwargs['timetable_id']})


class TimeTableResultView(DetailView):
    model = TimeTable
    template_name = 'scheduler/timetable/result.html'
    context_object_name = 'timetable'

    def get_queryset(self):
        return TimeTable.objects.select_related('organization')

    def get_object(self, queryset=None):
        return get_timetable_object(self, queryset=queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch all slots for the current timetable, pre-loading related data
        slots = Slot.objects.select_related(
            'section__group', 'date_time_slot', 'room', 'section__course', 'section__faculty'
        ).filter(section__timetable=self.object)

        # Group slots by the student group
        group_slots = defaultdict(list)
        for slot in slots:
            group_slots[slot.section.group].append(slot)

        # Prepare the data structure for the template
        organization = context['timetable'].organization
        days_range = range(1, organization.days_per_week + 1)
        time_range = range(1, organization.slots_per_day + 1)
        
        processed_timetables = []
        for group, group_slot_list in sorted(group_slots.items(), key=lambda item: item[0].group_id):
            # Create an empty timetable grid for the group
            table = {day: {time: None for time in time_range} for day in days_range}
            
            # Keep track of unique faculty for this group
            faculty_set = set()
            
            # Populate the grid with scheduled slots
            for slot in group_slot_list:
                if slot.date_time_slot:
                    day = slot.date_time_slot.day
                    time = slot.date_time_slot.time
                    if day in table and time in table[day]:
                        table[day][time] = slot
                        if slot.section.faculty:
                            faculty_set.add(slot.section.faculty)
            
            processed_timetables.append({
                'group': group,
                'table': table,
                'faculty_list': sorted(list(faculty_set), key=lambda f: f.name)
            })

        context['days'] = days_range
        context['time_slots'] = time_range
        context['processed_timetables'] = processed_timetables
        
        return context