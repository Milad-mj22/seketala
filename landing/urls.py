from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('api/voice-assistant/', views.voice_assistant, name='voice_assistant'),
]