from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from cameras import views



urlpatterns = [
    path('manage/', views.manage_cameras, name='manage_cameras'),  # Manage cameras
    path('add/', views.add_camera, name='add_camera'),  # Add camera page
    path('edit/<int:camera_id>/', views.edit_camera, name='edit_camera'),  # Edit camera page
    path('delete/<int:camera_id>/', views.delete_camera, name='delete_camera'),  # Delete camera action
    path('live-cameras/', views.live_cameras, name='live_cameras'),
    path('check-connectivity/', views.check_connectivity, name='check_connectivity'),
    path('camera/live/<int:camera_id>/', views.live_camera, name='live_camera'),  # View live camera feed
    path('detection/', views.detect_person, name='detect_person'),  # Detection page
    path('person/<int:person_id>/assign/', views.assign_person_to_user, name='assign_person_to_user'),  # Assign person
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)