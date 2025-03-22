from django.urls import path

from .views import GroupListView, GroupCreateView, GroupDetailView, GroupDeleteView, GroupUpdateView


urlpatterns = [
    path('', GroupListView.as_view(), name='group_list'),
    path('create/', GroupCreateView.as_view(), name='group_create'),
    path('<str:group_id>/', GroupDetailView.as_view(), name='group_detail'),
    path('<str:group_id>/delete', GroupDeleteView.as_view(), name='group_delete'),
    path('<str:group_id>/update', GroupUpdateView.as_view(), name='group_update'),
]