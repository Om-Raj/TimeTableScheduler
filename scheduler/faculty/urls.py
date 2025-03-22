from django.urls import path

from .views import FacultyListView, FacultyCreateView, FacultyDetailView, FacultyDeleteView, FacultyUpdateView


urlpatterns = [
    path('', FacultyListView.as_view(), name='faculty_list'),
    path('create/', FacultyCreateView.as_view(), name='faculty_create'),
    path('<int:pk>/', FacultyDetailView.as_view(), name='faculty_detail'),
    path('<int:pk>/delete', FacultyDeleteView.as_view(), name='faculty_delete'),
    path('<int:pk>/update', FacultyUpdateView.as_view(), name='faculty_update'),
]