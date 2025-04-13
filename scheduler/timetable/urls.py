from django.urls import path

from .views import TimeTableListView, TimeTableCreateView, TimeTableDetailView, TimeTableDeleteView, TimeTableUpdateView, SectionCreateView, TimetableScheduleView


urlpatterns = [
    path('', TimeTableListView.as_view(), name='timetable_list'),
    path('create/', TimeTableCreateView.as_view(), name='timetable_create'),
    path('<slug:timetable_id>/', TimeTableDetailView.as_view(), name='timetable_detail'),
    path('<slug:timetable_id>/delete', TimeTableDeleteView.as_view(), name='timetable_delete'),
    path('<slug:timetable_id>/update', TimeTableUpdateView.as_view(), name='timetable_update'),
    path('<slug:timetable_id>/add-section/', SectionCreateView.as_view(), name='section_create'),
    path('<slug:timetable_id>/schedule/', TimetableScheduleView.as_view(), name='timetable_schedule'),
]