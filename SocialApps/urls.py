# myapp/urls.py
from django.urls import path
from . import views


urlpatterns = [
    path('WA/<int:user_id>/', views.connect_whatsapp, name='connect_whatsapp'),
    path('WA/CollectMessages/<int:user_id>/', views.WA_get_messages, name='CollectMessages'),
]