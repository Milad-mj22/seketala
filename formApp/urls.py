
from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_form, name='create_form'),
    path('form/<int:form_id>/add-fields/', views.add_fields, name='add_fields'),
    path('form/<int:form_id>/submit/', views.submit_form, name='submit_form'),
    path('form/<int:form_id>/close/', views.close_form, name='close_form'),
    path('results/', views.form_results, name='form_results'),

    path('my-forms/', views.available_forms, name='available_forms'),

]
