from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse
from django.shortcuts import get_object_or_404

from .models import Room
from scheduler.organization.models import Organization
from scheduler.mixins import OrganizationContextMixin


# helper function to get room object
def get_room_object(self, queryset = None):
    if queryset is None:
        queryset = self.get_queryset()
    org_id = self.kwargs['org_id']
    room_id = self.kwargs['room_id']
    try:
        return queryset.get(organization__id=org_id, room_id=room_id)
    except:
        return Http404('Room not found')


# helper function to get success url
def get_room_success_url(self):
    return reverse('room_detail', kwargs={
        'org_id': self.object.organization.id,
        'room_id': self.object.room_id,
    })


class RoomListView(OrganizationContextMixin, ListView):
    model = Room
    template_name = 'scheduler/room/list.html'

    def get_queryset(self):
        return Room.objects.filter(organization__id=self.kwargs['org_id'])


class RoomCreateView(OrganizationContextMixin, CreateView):
    model = Room
    template_name = 'scheduler/room/create.html'
    fields = ('room_id', 'is_lab', 'capacity')

    def form_valid(self, form):
        form.instance.organization = get_object_or_404(Organization, id=self.kwargs['org_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('room_detail', kwargs={
            'org_id': self.object.organization.id,
            'room_id': self.object.room_id
        })


class RoomDetailView(OrganizationContextMixin, DetailView):
    model = Room
    template_name = 'scheduler/room/detail.html'
    slug_url_kwarg = 'room_id'
    slug_field = 'room_id'

    def get_queryset(self):
        return super().get_queryset().filter(organization_id=self.kwargs['org_id'])


class RoomDeleteView(OrganizationContextMixin, DeleteView):
    model = Room
    template_name = 'scheduler/room/delete.html'
    slug_url_kwarg = 'room_id'
    slug_field = 'room_id'

    def get_queryset(self):
        return super().get_queryset().filter(organization_id=self.kwargs['org_id'])

    def get_success_url(self):
        return reverse('room_list', kwargs={'org_id': self.kwargs['org_id']})


class RoomUpdateView(OrganizationContextMixin, UpdateView):
    model = Room
    template_name = 'scheduler/room/update.html'
    fields = ('is_lab', 'capacity')
    slug_url_kwarg = 'room_id'
    slug_field = 'room_id'

    def get_queryset(self):
        return super().get_queryset().filter(organization_id=self.kwargs['org_id'])

    def get_success_url(self):
        return reverse('room_detail', kwargs={
            'org_id': self.object.organization.id,
            'room_id': self.object.room_id
        })