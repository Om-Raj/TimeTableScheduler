from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse, reverse_lazy
from django.http import Http404

from .models import Room
from scheduler.organization.models import Organization


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


class RoomListView(ListView):
    model = Room
    template_name = 'scheduler/room/list.html'


class RoomCreateView(CreateView):
    model = Room
    template_name = 'scheduler/room/create.html'
    fields = ('room_id', 'is_lab', 'capacity')

    def get_success_url(self):
        return get_room_success_url(self)

    def form_valid(self, form):
        org_id = self.kwargs['org_id']
        form.instance.organization = Organization.objects.get(id=org_id)
        return super().form_valid(form)
    


class RoomDetailView(DetailView):
    model = Room
    template_name = 'scheduler/room/detail.html'

    def get_object(self, queryset = None):
        return get_room_object(self, queryset=queryset)


class RoomDeleteView(DeleteView):
    model = Room
    template_name = 'scheduler/room/delete.html'
    success_url = reverse_lazy('room_list')

    def get_object(self, queryset = None):
        return get_room_object(self, queryset=queryset)



class RoomUpdateView(UpdateView):
    model = Room
    template_name = 'scheduler/room/update.html'
    fields = ('room_id', 'is_lab', 'capacity')

    def get_success_url(self):
        return get_room_success_url(self)