from django.urls import path

from .views import TimeTableListView, TimeTableCreateView, TimeTableDetailView, TimeTableDeleteView, TimeTableUpdateView, SectionCreateView, TimeTableScheduleView, TimeTableResultView


urlpatterns = [
    path('', TimeTableListView.as_view(), name='timetable_list'),
    path('create/', TimeTableCreateView.as_view(), name='timetable_create'),
    path('<slug:timetable_id>/', TimeTableDetailView.as_view(), name='timetable_detail'),
    path('<slug:timetable_id>/delete', TimeTableDeleteView.as_view(), name='timetable_delete'),
    path('<slug:timetable_id>/update', TimeTableUpdateView.as_view(), name='timetable_update'),
    path('<slug:timetable_id>/add-section/', SectionCreateView.as_view(), name='section_create'),
    path('<slug:timetable_id>/schedule/', TimeTableScheduleView.as_view(), name='timetable_schedule'),
    path('<slug:timetable_id>/result/', TimeTableResultView.as_view(), name='timetable_result'),
]