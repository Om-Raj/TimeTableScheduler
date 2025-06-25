from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse
from django.shortcuts import get_object_or_404

from .models import Course
from scheduler.organization.models import Organization
from scheduler.mixins import OrganizationContextMixin
from scheduler.room.models import Room

# helper function to get course object
def get_course_object(self, queryset = None):
    if queryset is None:
        queryset = self.get_queryset()
    org_id = self.kwargs['org_id']
    course_id = self.kwargs['course_id']
    try:
        return queryset.get(organization__id=org_id, course_id=course_id)
    except:
        return Http404('Course not found')


# helper function to get success url
def get_course_success_url(self):
    return reverse('course_detail', kwargs={
        'org_id': self.object.organization.id,
        'course_id': self.object.course_id,
    })

class CourseListView(OrganizationContextMixin, ListView):
    model = Course
    template_name = 'scheduler/course/list.html'

    def get_queryset(self):
        return Course.objects.filter(organization__id=self.kwargs['org_id'])


class CourseCreateView(OrganizationContextMixin, CreateView):
    model = Course
    template_name = 'scheduler/course/create.html'
    fields = ('course_id', 'title', 'rooms')

    def form_valid(self, form):
        form.instance.organization = get_object_or_404(Organization, id=self.kwargs['org_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('course_detail', kwargs={
            'org_id': self.object.organization.id,
            'course_id': self.object.course_id
        })

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['rooms'].queryset = Room.objects.filter(organization__id=self.kwargs['org_id'])
        return form


class CourseDetailView(OrganizationContextMixin, DetailView):
    model = Course
    template_name = 'scheduler/course/detail.html'
    slug_url_kwarg = 'course_id'
    slug_field = 'course_id'

    def get_queryset(self):
        return super().get_queryset().filter(organization_id=self.kwargs['org_id'])


class CourseDeleteView(OrganizationContextMixin, DeleteView):
    model = Course
    template_name = 'scheduler/course/delete.html'
    slug_url_kwarg = 'course_id'
    slug_field = 'course_id'

    def get_queryset(self):
        return super().get_queryset().filter(organization_id=self.kwargs['org_id'])

    def get_success_url(self):
        return reverse('course_list', kwargs={'org_id': self.kwargs['org_id']})


class CourseUpdateView(OrganizationContextMixin, UpdateView):
    model = Course
    template_name = 'scheduler/course/update.html'
    fields = ('title', 'rooms')
    slug_url_kwarg = 'course_id'
    slug_field = 'course_id'

    def get_queryset(self):
        return super().get_queryset().filter(organization_id=self.kwargs['org_id'])

    def get_success_url(self):
        return reverse('course_detail', kwargs={
            'org_id': self.object.organization.id,
            'course_id': self.object.course_id
        })

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['rooms'].queryset = Room.objects.filter(organization__id=self.kwargs['org_id'])
        return form