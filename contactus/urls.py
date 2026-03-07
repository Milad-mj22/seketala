from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from users.views import contact_us



urlpatterns = [


    path("",contact_us,name='contact')

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


