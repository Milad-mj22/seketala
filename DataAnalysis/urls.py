from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from DataAnalysis import views



urlpatterns = [

    path('upload-db/', views.upload_db, name='upload_db'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('nahve/', views.calc_nahve_pardakh, name='calc_nahve_pardakht'),
    path("api/receive-invoice/", views.ReceiveInvoice.as_view()),
    path("api/receive-user/", views.ReceiveUser.as_view()),
    path("report/", views.invoice_report, name="invoice_report"),
    path("report/download/", views.download_invoice_excel, name="download_invoice_excel"),
    path("report/download-summary/", views.sepidar_download_excel, name="download_invoice_summary_excel"),
    path("report/tasvieh_download_summary/", views.tasvieh_sepidar_download_excel, name="tasvieh_download_invoice_summary_excel"),
    path("report/phone_numbers/", views.all_contancts_excel, name="phone_numbers"),
    path("api/invoices/<str:invoice_number>/",views.invoice_detail_api,name="invoice_detail_api"),
    path('factors/', views.factor_list, name='factor_list'),
    path('factors/<int:invoice_id>/', views.factor_detail, name='factor_detail'),
    path('factors/<int:invoice_id>/update-payments/', views.update_payments, name='update_payments'),
    path('api/factors/', views.api_factors, name='api_factors'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)