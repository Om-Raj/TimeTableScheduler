from django.urls import path, include

from .views import OrganizationListView, OrganizationCreateView, OrganizationDetailView, OrganizationDeleteView, OrganizationUpdateView


urlpatterns = [
    path('', OrganizationListView.as_view(), name='org_list'),
    path('create/', OrganizationCreateView.as_view(), name='org_create'),
    path('<int:org_id>/', OrganizationDetailView.as_view(), name='org_detail'),
    path('<int:org_id>/delete/', OrganizationDeleteView.as_view(), name='org_delete'),
    path('<int:org_id>/update/', OrganizationUpdateView.as_view(), name='org_update'),
    path('<int:org_id>/course/', include('scheduler.course.urls')),
    path('<int:org_id>/faculty/', include('scheduler.faculty.urls')),
    path('<int:org_id>/group/', include('scheduler.group.urls')),
    path('<int:org_id>/room/', include('scheduler.room.urls')),
    path('<int:org_id>/timetable/', include('scheduler.timetable.urls')),
]