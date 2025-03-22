from django.urls import path, include

from .views import SchedulerHomeView


urlpatterns = [
    path('', SchedulerHomeView.as_view(), name='scheduler_home'),
    path('org/', include('scheduler.organization.urls')),
]