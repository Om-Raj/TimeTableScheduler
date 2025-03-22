from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse, reverse_lazy
from django.http import Http404

from .models import Group
from scheduler.organization.models import Organization


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


class GroupListView(ListView):
    model = Group
    template_name = 'scheduler/group/list.html'

    def get_queryset(self):
        org_id = self.kwargs['org_id']
        return Group.objects.filter(organization__id=org_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['organization'] = Organization.objects.get(id=self.kwargs['org_id'])
        return context


class GroupCreateView(CreateView):
    model = Group
    template_name = 'scheduler/group/create.html'
    fields = ('group_id', 'size')

    def get_success_url(self):
        return get_group_success_url(self)

    def form_valid(self, form):
        org_id = self.kwargs['org_id']
        form.instance.organization = Organization.objects.get(id=org_id)
        return super().form_valid(form)
    


class GroupDetailView(DetailView):
    model = Group
    template_name = 'scheduler/group/detail.html'

    def get_object(self, queryset = None):
        return get_group_object(self, queryset=queryset)


class GroupDeleteView(DeleteView):
    model = Group
    template_name = 'scheduler/group/delete.html'

    def get_object(self, queryset = None):
        return get_group_object(self, queryset=queryset)

    def get_success_url(self):
        return reverse('group_list', kwargs={'org_id': self.kwargs['org_id']})



class GroupUpdateView(UpdateView):
    model = Group
    template_name = 'scheduler/group/update.html'
    fields = ('group_id', 'size')

    def get_object(self, queryset = None):
        return get_group_object(self, queryset=queryset)

    def get_success_url(self):
        return get_group_success_url(self)
