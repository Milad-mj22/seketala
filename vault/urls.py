from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


app_name = "vault"

urlpatterns = [
    path("login/", views.simple_login, name="simple_login"),
    path("logout/", views.simple_logout, name="simple_logout"),

    path("", views.dashboard, name="dashboard"),
    path("passwords/", views.password_list, name="password_list"),
    path("passwords/new/", views.password_create, name="password_create"),
    path("passwords/<int:pk>/edit/", views.password_edit, name="password_edit"),
    path("passwords/<int:pk>/", views.password_detail, name="password_detail"),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
