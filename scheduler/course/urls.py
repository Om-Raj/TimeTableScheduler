from django.urls import path

from .views import CourseListView, CourseCreateView, CourseDetailView, CourseDeleteView, CourseUpdateView


urlpatterns = [
    path('', CourseListView.as_view(), name='course_list'),
    path('create/', CourseCreateView.as_view(), name='course_create'),
    path('<int:pk>/', CourseDetailView.as_view(), name='course_detail'),
    path('<int:pk>/delete', CourseDeleteView.as_view(), name='course_delete'),
    path('<int:pk>/update', CourseUpdateView.as_view(), name='course_update'),
]