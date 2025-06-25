from collections import defaultdict

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, FormView
from django.urls import reverse, reverse_lazy
from django.http import Http404
from django.shortcuts import get_object_or_404

from scheduler.organization.models import Organization
from scheduler.timetable.tasks import run_scheduler_task
from scheduler.mixins import OrganizationContextMixin

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


class TimeTableListView(OrganizationContextMixin, ListView):
    model = TimeTable
    template_name = 'scheduler/timetable/list.html'

    def get_queryset(self):
        return TimeTable.objects.filter(organization__id=self.kwargs['org_id'])


class SectionCreateView(OrganizationContextMixin, CreateView):
    model = Section
    fields = ('faculty', 'course', 'group', 'duration')
    template_name = 'scheduler/section/create.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        org = get_object_or_404(Organization, id=self.kwargs['org_id'])
        form.fields['faculty'].queryset = Faculty.objects.filter(organization=org)
        form.fields['course'].queryset = Course.objects.filter(organization=org)
        form.fields['group'].queryset = Group.objects.filter(organization=org)
        return form

    def form_valid(self, form):
        timetable = get_object_or_404(
            TimeTable,
            organization__id=self.kwargs['org_id'],
            timetable_id=self.kwargs['timetable_id']
        )
        form.instance.timetable = timetable
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['timetable_id'] = self.kwargs['timetable_id']
        return context

    def get_success_url(self):
        return reverse(
            'timetable_detail',
            kwargs={
                'org_id': self.kwargs['org_id'],
                'timetable_id': self.kwargs['timetable_id']
            }
        )


class TimeTableCreateView(OrganizationContextMixin, CreateView):
    model = TimeTable
    template_name = 'scheduler/timetable/create.html'
    fields = ('year', 'semester')

    def form_valid(self, form):
        form.instance.organization = get_object_or_404(Organization, id=self.kwargs['org_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('timetable_detail', kwargs={
            'org_id': self.object.organization.id,
            'timetable_id': self.object.timetable_id
        })


class TimeTableDetailView(OrganizationContextMixin, DetailView):
    model = TimeTable
    template_name = 'scheduler/timetable/detail.html'
    context_object_name = 'timetable'
    slug_url_kwarg = 'timetable_id'
    slug_field = 'timetable_id'

    def get_queryset(self):
        return super().get_queryset().filter(organization_id=self.kwargs['org_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sections'] = Section.objects.filter(timetable=self.object)
        context['status'] = ScheduleStatus.objects.filter(timetable=self.object).first()
        return context


class TimeTableDeleteView(OrganizationContextMixin, DeleteView):
    model = TimeTable
    template_name = 'scheduler/timetable/delete.html'
    slug_url_kwarg = 'timetable_id'
    slug_field = 'timetable_id'

    def get_queryset(self):
        return super().get_queryset().filter(organization_id=self.kwargs['org_id'])

    def get_success_url(self):
        return reverse('timetable_list', kwargs={'org_id': self.kwargs['org_id']})


class TimeTableUpdateView(OrganizationContextMixin, UpdateView):
    model = TimeTable
    template_name = 'scheduler/timetable/update.html'
    fields = ('year', 'semester')
    slug_url_kwarg = 'timetable_id'
    slug_field = 'timetable_id'

    def get_queryset(self):
        return super().get_queryset().filter(organization_id=self.kwargs['org_id'])

    def get_success_url(self):
        return reverse('timetable_detail', kwargs={
            'org_id': self.object.organization.id,
            'timetable_id': self.object.timetable_id
        })


class TimeTableScheduleView(OrganizationContextMixin, FormView):
    form_class = RunSchedulerForm
    template_name = 'scheduler/timetable/schedule.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['timetable'] = get_object_or_404(
            TimeTable,
            organization__id=self.kwargs['org_id'],
            timetable_id=self.kwargs['timetable_id']
        )
        return context

    def form_valid(self, form):
        org_id = self.kwargs['org_id']
        timetable_id = self.kwargs['timetable_id']
        task = run_scheduler_task.delay(org_id, timetable_id)

        timetable = get_object_or_404(
            TimeTable,
            organization__id=org_id,
            timetable_id=timetable_id
        )
        status, _ = ScheduleStatus.objects.get_or_create(timetable=timetable)
        status.status = "PENDING"
        status.task_id = task.id
        status.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('timetable_detail', kwargs={
            'org_id': self.kwargs['org_id'],
            'timetable_id': self.kwargs['timetable_id']
        })


class TimeTableResultView(OrganizationContextMixin, DetailView):
    model = TimeTable
    template_name = 'scheduler/timetable/result.html'
    context_object_name = 'timetable'
    slug_url_kwarg = 'timetable_id'
    slug_field = 'timetable_id'

    def get_queryset(self):
        return TimeTable.objects.select_related('organization').filter(organization_id=self.kwargs['org_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slots = Slot.objects.select_related(
            'section__group', 'date_time_slot', 'room', 'section__course', 'section__faculty'
        ).filter(section__timetable=self.object)

        group_slots = defaultdict(list)
        for slot in slots:
            group_slots[slot.section.group].append(slot)

        organization = context['timetable'].organization
        days_range = range(1, organization.days_per_week + 1)
        time_range = range(1, organization.slots_per_day + 1)
        
        processed_timetables = []
        for group, group_slot_list in sorted(group_slots.items(), key=lambda item: item[0].group_id):
            table = {day: {time: None for time in time_range} for day in days_range}
            
            faculty_set = set()
            
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

        context['processed_timetables'] = processed_timetables
        context['days_range'] = days_range
        context['time_range'] = time_range

        return context