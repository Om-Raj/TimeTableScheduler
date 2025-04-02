from django.urls import path

from .views import TimeTableListView, TimeTableCreateView, TimeTableDetailView, TimeTableDeleteView, TimeTableUpdateView, SlotCreateView


urlpatterns = [
    path('', TimeTableListView.as_view(), name='timetable_list'),
    path('create/', TimeTableCreateView.as_view(), name='timetable_create'),
    path('<int:timetable_id>/', TimeTableDetailView.as_view(), name='timetable_detail'),
    path('<int:pk>/delete', TimeTableDeleteView.as_view(), name='timetable_delete'),
    path('<int:pk>/update', TimeTableUpdateView.as_view(), name='timetable_update'),
    path('<int:timetable_id>/add-slot/', SlotCreateView.as_view(), name='slot_create'),
]