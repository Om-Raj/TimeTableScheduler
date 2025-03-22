from django.views.generic import TemplateView


class SchedulerHomeView(TemplateView):
    template_name = 'scheduler/home.html'