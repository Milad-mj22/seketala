
from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_form, name='create_form'),
    path('form/<int:form_id>/add-fields/', views.add_fields, name='add_fields'),
    path('form/<int:form_id>/submit/', views.submit_form, name='submit_form'),
    path('form/<int:form_id>/close/', views.close_form, name='close_form'),
    path('results/', views.form_results, name='form_results'),

    path('my-forms/', views.available_forms, name='available_forms'),


    path('night_form_create/', views.nightly_sales_view, name='available_forms'),
    path('form/<int:form_id>/', views.form_detail, name='form_detail'),
    
    path('nightforms/', views.NightlyFormListView.as_view(), name='nightly_forms_list'),
    path('nightforms/download/<int:form_id>/', views.download_excel, name='download_excel'),


    path('nightforms/peyk_create/', views.peyk_create, name='peyk_create'),
    path('api/people/', views.get_people, name='get_people'),
    
]
