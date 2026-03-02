from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from FoodPrice import views




urlpatterns = [
    path("", views.foods_list, name="foods_list"),
    path("foods/add/", views.add_food, name="add_food"),
    path("foods/ingredient/delete/<int:ingredient_id>/", views.delete_food_ingredient, name="delete_food_ingredient"),
    
    
    path("foods/<int:food_id>/ingredients/", views.food_ingredients, name="food_ingredients"),
    path('ingredients/<int:ingredient_id>/delete/', views.delete_ingredient, name='delete_ingredient'),
    path('ingredient/<int:ingredient_id>/update/', views.update_ingredient, name='update_ingredient'),
    path('foods/<int:food_id>/ingredient/add/', views.add_ingredient, name='add_ingredient'),
    path("foods/<int:food_id>/delete/", views.delete_food, name="delete_food"),
    path('foods/<int:pk>/edit/', views.update_food, name='update_food'),
    path('foods/add/', views.add_food, name='add_food'),


]
