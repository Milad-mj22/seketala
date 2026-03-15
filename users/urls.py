from django.urls import path
from .views import  add_buyer_activity, add_material_to_category, buyer_activity_detail, buyer_attr_manage, buyer_dashboard, buyer_dashboard_partial, buyer_dashboard_view, buyer_detail, buyer_login_view, buyer_logout_view, categories_list, category_create, category_delete, category_detail, category_list, category_update, confirm_delete_buyer_request, confirm_delete_view, confirm_purchase_view, delete_buyer_activity, edit_buyer_activity, logout_view, material_composition_view_first, mother_material_add, mother_material_edit, mother_material_list, otp_send, otp_verify, post_login_redirect, raw_material_add, raw_material_delete, raw_material_edit, raw_material_list, reject_delete_buyer_request, remove_material_from_category, review_delete_buyers_requests, show_factor,create_user_view, daily_report_view, delete_buyer, delete_buyer_attribute, delete_user, edit_user, error_page, home, job_create_view, job_delete_view, job_edit_view, job_list_view, manage_role_access, material_composition_view, no_access, profile, RegisterView, send_test_notification, show_menu_options,tools \
        ,my_orders,add_raw_material,post_edit_quil\
        ,create_order,add_mother_material,show_order,snapp,show_restaurant_list,\
        restaurant_food_list,add_restaurant,print_order,foodRawMaterials,addfoodrawmaterial,show_food_material,night_food_order,\
        load_temp,CustomLogoutView,add_store,success_page,\
        show_store,submit_data,show_test,take_store,confrim_take_store,log_view_store,\
        register_entry,register_exit,get_allowed_locations,histoty_entry,update_prices, show_night_order_material,\
        add_buyer,edit_buyer,buyer_list , subscribe , send_test_notification, user_list_view 

from menu.views import set_sold_out
        
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', home, name='users-home'),
    path('redirect_after_login/', post_login_redirect, name='post_login_redirect'),
    path('register/', RegisterView.as_view(), name='users-register'),

    path("logout/", logout_view, name="logout"),
    path('profile/', profile, name='users-profile'),
    path('tools/',tools, name='tools'),
    path('tools/snapp',snapp, name='tools'),
    path('tools/foodrawmaterials',foodRawMaterials, name='foodRawMaterials'),
    path('tools/foodrawmaterials/<int:id>',show_food_material, name='foodRawMaterials'),
    path('tools/add_food_raw_material',addfoodrawmaterial, name='addfoodrawmaterial'),

    # path('tools/snapp/اصفهان/<str:res_name>',restaurant_food_list, name='tools'),

    
    path('tools/snapp/add_restaurant',add_restaurant, name='tools'),
    path('tools/snapp/<str:city>',show_restaurant_list, name='tools'),
    # path('tools/snapp/<str:city>/<str:res_name>',restaurant_food_list, name='tools'),
    path('tools/snapp/<str:city>/<str:res_name>',restaurant_food_list, name='tools'),
    path('tools/snapp/<str:city>/<str:res_name>/update_prices',update_prices, name='tools'),
    path('tools/menu',show_menu_options, name='tools'),
    path('tools/settingmenu',set_sold_out, name='tools'),


    path('orders/print_order/<int:id>', print_order, name='order-show'),





    path('mother-materials/', mother_material_list, name='mother_material_list'),
    path('mother-materials/add/', mother_material_add, name='mother_material_add'),
    path('mother-materials/<int:pk>/edit/', mother_material_edit, name='mother_material_edit'),
    path('mother-materials/<int:pk>/delete/', confirm_delete_view, name='mother_material_delete'),


    # Raw material urls
    path('raw-materials/', raw_material_list, name='raw_material_list'),
    path('raw-materials/add/', raw_material_add, name='raw_material_add'),
    path('raw-materials/edit/<int:pk>/', raw_material_edit, name='raw_material_edit'),
    path('raw-materials/delete/<int:pk>/', raw_material_delete, name='raw_material_delete'),
    
    path('profile/create_order', create_order, name='create_post'),
    path('profile/my_orders', my_orders, name='my_posts'),
    path('profile/create_material/', add_raw_material, name='add_material'),
    path('profile/create_mother_material/', add_mother_material, name='add_mother_material'),
    path('profile/night_order/', night_food_order, name='night_food_order'),
    path('profile/night_order/null', night_food_order, name='night_food_order'),
    path('profile/show_night_order_material', show_night_order_material, name='show_night_order_material'),
    path('profile/show_night_order_material/submit', night_food_order, name='show_night_order_material_submit'),
    # path('tools/<slug:slug>/',PostDetail.as_view(), name='post_detail'),
    path('orders/edit_order/<int:id>', post_edit_quil, name='order-edit'),
    path('orders/show_order/<int:id>', show_order, name='order-show'),
    path('posts/<int:id>/', post_edit_quil, name='post-edit'),
    path('test/', load_temp, name='post-create3'),

    ################### STORE
    path('profile/store_add/',add_store,name='add-store'),
    path('profile/store_product/',material_composition_view,name='product-store'),
    path('profile/store_product_first/',material_composition_view_first,name='product-store_first'),
    path('profile/store_take/',take_store,name='add-store'),
    path('profile/store_take_confirm/',confrim_take_store,name='add-store'),
    path('profile/store/',show_store,name='add-store'),
    path('profile/store_log/', log_view_store, name='logs_store'),
    # path('profile/store_product/', product_store, name='product_store'),
    #////////////////////////////////////
# profile/{{user.id}}/register_entry
    path('profile/<int:id>/register_entry/', register_entry, name='register_entry'),
    path('profile/<int:id>/history_entry/', histoty_entry, name='register_entry'),
    # path('profile/<int:id>/register_entry/', register_exit, name='register_exit'),
    path('get_allowed_locations/', get_allowed_locations, name='register_entry'),
    path('profile/daily-report/', daily_report_view, name='daily_report'),
    path('profile/daily-report/edit/<int:pk>/', edit_buyer_activity, name='edit_buyer_activity'),
    path('profile/daily-report/delete/<int:pk>/', delete_buyer_activity, name='delete_buyer_activity'),
    



    path('success/', success_page, name='success_page'),  # URL for success page
    path('error/', error_page, name='error_page'),  # URL for error page
    path('submit-warehouse/', show_store, name='submit-warehouse'),
    path('submit-data/', submit_data, name='submit_data'),
    path('show_test/', show_test, name='submit_data'),
    #/////////////////////////
    path('no_access/', no_access, name='no_access'),



    path("subscribe/", subscribe, name="subscribe"),
    path("send-test-notification/", send_test_notification, name="send_test_notification"),
    





    path('buyers/', buyer_list, name='buyer_list'),
    path('buyers/add/', add_buyer, name='add_buyer'),
    path('buyers/edit/<int:pk>/', edit_buyer, name='edit_buyer'),
    path('buyers/delete/<int:buyer_id>/', delete_buyer, name='delete_buyer'),
    path('buyers/details/<int:buyer_id>/', buyer_detail, name='buyer_detail'),
    path('buyers/activity/<int:buyer_id>/<str:activity_type>/', buyer_activity_detail, name='buyer_activity_detail'),
    path('buyers/delete/<int:buyer_id>/', confirm_delete_buyer_request, name='confirm_delete_buyer_request'),
    path('buyers/reject_delete/<int:buyer_id>/', reject_delete_buyer_request, name='reject_buyer_delete'),
    path('buyers/<int:buyer_id>/add-activity/', add_buyer_activity, name='add_buyer_activity'),
    path('buyers/admin/review_delete_buyers_requests/', review_delete_buyers_requests, name='review_delete_buyers_requests'),

    path('buyers/dashboard/', buyer_dashboard, name='buyer_dashboard'),
    path('buyers/dashboard_partial/', buyer_dashboard_partial, name='buyer_dashboard_partial'),
    # path('buyers/login/', auth_views.LoginView.as_view(template_name='Buyer/buyer_login.html'), name='login'),
    # path('buyers/logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),


    path('buyers/login/', buyer_login_view, name='buyer_login'),
    path('buyers/dashboard_person/', buyer_dashboard_view, name='person_buyer_dashboard'),
    path('buyers/logout/',buyer_logout_view, name='buyer_logout'),
    path('buyers/confirm/<int:log_id>/', confirm_purchase_view, name='confirm_purchase'),
    path('buyers/factor/<int:pk>/', show_factor, name='show_factor'),

    path('buyers/admin/categories/', category_list, name='category_list'),
    path('buyers/admin/categories/create/', category_create, name='category_create'),
    path('buyers/admin/categories/<int:pk>/edit/', category_update, name='category_update'),
    path('buyers/admin/categories/<int:pk>/delete/', category_delete, name='category_delete'),


    

    path('users/admin/create-user/', create_user_view, name='create_user'),
    path('users/admin/users/', user_list_view, name='user_list'),
    path('users/admin/edit/<int:user_id>/', edit_user, name='edit_user'),
    path('users/admin/delete/<int:user_id>/', delete_user, name='delete_user'),

    path('users/admin/jobs/', job_list_view, name='job_list'),
    path('users/admin/jobs/create/', job_create_view, name='job_create'),
    path('users/admin/jobs/edit/<int:pk>/', job_edit_view, name='job_edit'),
    path('users/admin/jobs/delete/<int:pk>/', job_delete_view, name='job_delete'),



    path('buyer-attributes/admin/', buyer_attr_manage, name='buyer_attr_manage'),
    path('buyer-attributes/admin/delete/<int:attr_id>/', delete_buyer_attribute, name='delete_buyer_attribute'),

    path('manage_role_access/admin/', manage_role_access, name='manage_role_access'),


    path('auth/otp/send/', otp_send, name='otp-send'),
    path('auth/otp/verify/', otp_verify, name='otp-verify'),

    path("categories/", categories_list, name="categories_list"),
    path("categories/<int:category_id>/", category_detail, name="category_detail"),
    path("categories/<int:category_id>/add-material/", add_material_to_category, name="add_material_to_category"),
    path("category/<int:category_id>/remove/<int:material_id>/",
        remove_material_from_category,
        name="remove_material_from_category"),


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



from django.views.static import serve as serve_static
from django.urls import re_path
from django.conf import settings


urlpatterns += [
    re_path(r'^sw\.js$', serve_static, {
        'path': 'sw.js',  # مسیر فایل کنار manage.py
        'document_root': settings.BASE_DIR
    }),
]