from django.urls import path

from .views import CourseListView, CourseCreateView, CourseDetailView, CourseDeleteView, CourseUpdateView


urlpatterns = [
    path('', CourseListView.as_view(), name='course_list'),
    path('create/', CourseCreateView.as_view(), name='course_create'),
    path('<str:course_id>/', CourseDetailView.as_view(), name='course_detail'),
    path('<str:course_id>/delete', CourseDeleteView.as_view(), name='course_delete'),
    path('<str:course_id>/update', CourseUpdateView.as_view(), name='course_update'),
]