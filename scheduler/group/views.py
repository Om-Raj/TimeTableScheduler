from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse
from django.shortcuts import get_object_or_404

from .models import Group
from scheduler.organization.models import Organization
from scheduler.mixins import OrganizationContextMixin


# helper function to get group object
def get_group_object(self, queryset = None):
    if queryset is None:
        queryset = self.get_queryset()
    org_id = self.kwargs['org_id']
    group_id = self.kwargs['group_id']
    try:
        return queryset.get(organization__id=org_id, group_id=group_id)
    except:
        return Http404('Group not found')


# helper function to get success url
def get_group_success_url(self):
    return reverse('group_detail', kwargs={
        'org_id': self.object.organization.id,
        'group_id': self.object.group_id,
    })


class GroupListView(OrganizationContextMixin, ListView):
    model = Group
    template_name = 'scheduler/group/list.html'

    def get_queryset(self):
        return Group.objects.filter(organization__id=self.kwargs['org_id'])


class GroupCreateView(OrganizationContextMixin, CreateView):
    model = Group
    template_name = 'scheduler/group/create.html'
    fields = ('group_id', 'size')

    def form_valid(self, form):
        form.instance.organization = get_object_or_404(Organization, id=self.kwargs['org_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('group_detail', kwargs={
            'org_id': self.object.organization.id,
            'group_id': self.object.group_id
        })


class GroupDetailView(OrganizationContextMixin, DetailView):
    model = Group
    template_name = 'scheduler/group/detail.html'
    slug_url_kwarg = 'group_id'
    slug_field = 'group_id'

    def get_queryset(self):
        return super().get_queryset().filter(organization_id=self.kwargs['org_id'])


class GroupDeleteView(OrganizationContextMixin, DeleteView):
    model = Group
    template_name = 'scheduler/group/delete.html'
    slug_url_kwarg = 'group_id'
    slug_field = 'group_id'

    def get_queryset(self):
        return super().get_queryset().filter(organization_id=self.kwargs['org_id'])

    def get_success_url(self):
        return reverse('group_list', kwargs={'org_id': self.kwargs['org_id']})


class GroupUpdateView(OrganizationContextMixin, UpdateView):
    model = Group
    template_name = 'scheduler/group/update.html'
    fields = ('size',)
    slug_url_kwarg = 'group_id'
    slug_field = 'group_id'

    def get_queryset(self):
        return super().get_queryset().filter(organization_id=self.kwargs['org_id'])

    def get_success_url(self):
        return reverse('group_detail', kwargs={
            'org_id': self.object.organization.id,
            'group_id': self.object.group_id
        })
