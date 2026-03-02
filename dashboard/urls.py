from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from dashboard.views import dashboard_employ_activity, mian_dashboard, preinvoice_ration_sell_user_report, preinvoice_user_report



urlpatterns = [


    path('', mian_dashboard, name='mian_dashboard'),
    path('dashboard_employ_activity/', dashboard_employ_activity, name='dashboard_employ_activity'),
    path('dashboard_preinvoice/', preinvoice_user_report, name='preinvoice_user_report'),
    path('dashboard_ratio_sell_preinvoice/', preinvoice_ration_sell_user_report, name='preinvoice_ration_sell_user_report'),




]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
