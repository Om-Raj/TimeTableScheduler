from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse, reverse_lazy

from .models import Faculty


class FacultyListView(ListView):
    model = Faculty
    template_name = 'scheduler/faculty/list.html'


class FacultyCreateView(CreateView):
    model = Faculty
    template_name = 'scheduler/faculty/create.html'
    fields = ('faculty_id', 'name', 'priority', 'slot_choices')

    def get_success_url(self):
        return reverse('faculty_detail', kwargs={'pk': self.object.pk})


class FacultyDetailView(DetailView):
    model = Faculty
    template_name = 'scheduler/faculty/detail.html'


class FacultyDeleteView(DeleteView):
    model = Faculty
    template_name = 'scheduler/faculty/delete.html'
    success_url = reverse_lazy('faculty_list')


class FacultyUpdateView(UpdateView):
    model = Faculty
    template_name = 'scheduler/faculty/update.html'
    fields = ('faculty_id', 'name', 'priority', 'slot_choices')

    def get_success_url(self):
        return reverse('faculty_detail', kwargs={'pk': self.object.pk})

