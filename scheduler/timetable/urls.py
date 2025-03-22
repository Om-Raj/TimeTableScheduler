from django.urls import path

from .views import TimeTableListView, TimeTableCreateView, TimeTableDetailView, TimeTableDeleteView, TimeTableUpdateView


urlpatterns = [
    path('', TimeTableListView.as_view(), name='timetable_list'),
    path('create/', TimeTableCreateView.as_view(), name='timetable_create'),
    path('<int:pk>/', TimeTableDetailView.as_view(), name='timetable_detail'),
    path('<int:pk>/delete', TimeTableDeleteView.as_view(), name='timetable_delete'),
    path('<int:pk>/update', TimeTableUpdateView.as_view(), name='timetable_update'),
]