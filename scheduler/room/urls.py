from django.urls import path

from .views import RoomListView, RoomCreateView, RoomDetailView, RoomDeleteView, RoomUpdateView


urlpatterns = [
    path('', RoomListView.as_view(), name='room_list'),
    path('create/', RoomCreateView.as_view(), name='room_create'),
    path('<str:room_id>/', RoomDetailView.as_view(), name='room_detail'),
    path('<str:room_id>/delete', RoomDeleteView.as_view(), name='room_delete'),
    path('<str:room_id>/update', RoomUpdateView.as_view(), name='room_update'),
]