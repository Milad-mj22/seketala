from django.urls import path
from . import views


from django.urls import path

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.mine_list, name='mine_list'),
    path('add/', views.add_mine, name='add_mine'),
    path('edit/<int:mine_id>/', views.edit_mine, name='edit_mine'),
    path('delete/<int:mine_id>/', views.delete_mine, name='delete_mine'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
