from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from .views import contact_us, submit_feedback
from . import views


urlpatterns = [
    path("",contact_us,name='contact'),
    path('api/submit-feedback/', submit_feedback, name='submit_feedback'),
    path('cards/', views.bank_card_list, name='bank_card_list'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


