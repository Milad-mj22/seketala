from django.urls import path

from .views import edit_request, section1_view,section2_view,section3_view,section4_view,\
                    show_flow
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [


    path('orders/show_flow/<int:order_id>', show_flow, name='show_flow'),

    path('section1/<int:order_id>/', section1_view, name='section1_url'),
    path('section2/<int:order_id>/', section2_view, name='section2_url'),
    path('section3/<int:order_id>/', section3_view, name='section3_url'),
    path('section4/<int:order_id>/', section4_view, name='section4_url'),


    path('edit-request/<int:order_id>/<int:step_number>/', edit_request, name='edit_request')


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
