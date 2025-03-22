from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse, reverse_lazy

from .models import Course


class CourseListView(ListView):
    model = Course
    template_name = 'scheduler/course/list.html'


class CourseCreateView(CreateView):
    model = Course
    template_name = 'scheduler/course/create.html'
    fields = ('course_id', 'title', 'rooms')

    def get_success_url(self):
        return reverse('course_detail', kwargs={'pk': self.object.pk})


class CourseDetailView(DetailView):
    model = Course
    template_name = 'scheduler/course/detail.html'


class CourseDeleteView(DeleteView):
    model = Course
    template_name = 'scheduler/course/delete.html'
    success_url = reverse_lazy('course_list')


class CourseUpdateView(UpdateView):
    model = Course
    template_name = 'scheduler/course/update.html'
    fields = ('course_id', 'title', 'rooms')

    def get_success_url(self):
        return reverse('course_detail', kwargs={'pk': self.object.pk})

