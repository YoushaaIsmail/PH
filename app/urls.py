
from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static
app_name = 'app'

urlpatterns = [
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_create, name='category_create'),
    path('categories/<uuid:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<uuid:pk>/delete/', views.category_delete, name='category_delete'),
        path('ingredients/', views.ingredient_list, name='ingredient_list'),
    path('ingredients/add/', views.ingredient_create, name='ingredient_create'),
    path('ingredients/<uuid:pk>/edit/', views.ingredient_edit, name='ingredient_edit'),
    path('ingredients/<uuid:pk>/delete/', views.ingredient_delete, name='ingredient_delete'),
    path('medicines/', views.medicine_list, name='medicine_list'),
path('medicines/add/', views.medicine_create, name='medicine_create'),
path('medicines/<uuid:pk>/edit/', views.medicine_edit, name='medicine_edit'),
path('medicines/<uuid:pk>/delete/', views.medicine_delete, name='medicine_delete'),
    path('prescriptions/', views.prescription_list, name='prescription_list'),
    path('prescriptions/add/', views.prescription_create, name='prescription_create'),
    path('prescriptions/<uuid:pk>/edit/', views.prescription_edit, name='prescription_edit'),
    path('prescriptions/<uuid:pk>/delete/', views.prescription_delete, name='prescription_delete'),
    path('addresses/', views.address_list, name='address_list'),
    path('addresses/add/', views.address_create, name='address_create'),
    path('addresses/<uuid:pk>/edit/', views.address_edit, name='address_edit'),
    path('addresses/<uuid:pk>/delete/', views.address_delete, name='address_delete'),
        path('ordersA/', views.order_listA, name='order_listA'),
              path('calculate-delivery/', views.calculate_delivery, name='calculate_delivery'),
                  path('upload-prescription/', views.upload_prescription, name='upload_prescription'),
    
    path('ordersA/add/', views.order_create, name='order_createA'),
    path('ordersA/<uuid:pk>/edit/', views.order_edit, name='order_edit'),
    path('ordersA/<uuid:pk>/delete/', views.order_delete, name='order_deleteA'),
   path('order_itemA/<uuid:order_id>/', views.order_item_list, name='order_item_list'),
       path('orderA/<uuid:order_id>/item/create/', views.order_item_create, name='order_item_create'),
    path('orderA/<uuid:order_id>/item/<uuid:item_id>/edit/', views.order_item_edit, name='order_item_edit'),
        # path('orderA/<uuid:order_id>/edit/', views.order_edit, name='order_edit'),
    path('orderA/<uuid:order_id>/item/<uuid:item_id>/delete/', views.order_item_delete, name='order_item_delete'),
        path('login/', views.login_view, name='login'),
            path('forget-password/', views.forget_password, name='forget_password'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('logout/', views.logout_view, name='logout'),
    path('change-password/', views.change_password, name='change_password'),
        path('registerCus/', views.registerCus, name='registerCus'),
        path('loginCus/', views.loginCus, name='loginCus'),
         path('Regcode/', views.Regcode, name='Regcode'),
         path('home/', views.medicine_show, name='home'),
             path('profile/', views.profile_view, name='profile'),
         path('medicine_show/', views.medicine_show, name='medicine_show'),
          path('about/edit/', views.about_edit, name='about_edit'),
              path('batchmed/', views.batchmed_list, name='batchmed_list'),
    path('batchmed/create/', views.batchmed_create, name='batchmed_create'),
    path('batchmed/<int:pk>/', views.batchmed_detail, name='batchmed_detail'),
    path('batchmed/<int:pk>/edit/', views.batchmed_edit, name='batchmed_edit'),
    path('batchmed/<int:pk>/delete/', views.batchmed_delete, name='batchmed_delete'),

    path('medicines/', views.medicine_list, name='medicine_list'),

    
    path('medicine/<uuid:medicine_id>/comments/', views.medicine_comments, name='medicine_comments'),
       path('medicine/<uuid:medicine_id>/addcomments/', views.add_comment, name='add_comment'),
   
        path('account/', views.account_dashboard, name='account_dashboard'),
    path('account/add/', views.add_money, name='add_money'),
    path('account/withdraw/', views.withdraw_money, name='withdraw_money'),
    path('account/history/', views.transaction_history, name='transaction_history'),

        path('medicine/<uuid:medicine_id>/', views.medicine_detail, name='medicine_detail'),
    path('add-to-cart/<uuid:medicine_id>/', views.add_to_cart, name='add_to_cart'),



        path('orders/', views.order_list, name='order_list'),
    path('orders/<uuid:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<uuid:order_id>/items/', views.order_items, name='order_items'),
    path('orders/<uuid:order_id>/pay/', views.order_payment, name='order_payment'),
    path('order-items/<uuid:item_id>/update/', views.update_order_item, name='update_order_item'),
    path('order-items/<uuid:item_id>/delete/', views.delete_order_item, name='delete_order_item'),
    path('orders/<uuid:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    # path('orders/<uuid:order_id>/locations/', views.get_order_locations, name='order_locations'),
    path('orders/<uuid:order_id>/locations/', views.order_locations_page, name='order_locations'),
    path('api/order/<uuid:order_id>/driver-location/', views.get_driver_location, name='get_driver_location'),
        path('operation/', views.operation_list, name='operation_list'),
            path('operations/<int:pk>/approve/', views.operation_approve, name='operation_approve1'),
    path('operations/<int:pk>/reject/', views.operation_reject, name='operation_reject1'),
        path('operations/<int:pk>/approve-withdraw/', views.operation_approve_withdraw, name='operation_approve_withdraw'),


    path('drivers/', views.driver_list, name='driver_list'),
    path('drivers/create/', views.driver_create, name='driver_create'),
    path('drivers/<int:pk>/edit/', views.driver_edit, name='driver_edit'),
    path('drivers/<int:pk>/delete/', views.driver_delete, name='driver_delete'),

         
path('driver/login/', views.driver_login, name='driver_login'),
    path('driver/dashboard/', views.driver_dashboard, name='driver_dashboard'),
    path('driver/logout/', views.driver_logout, name='driver_logout'),
    path('driver/update-location/', views.update_driver_location, name='update_driver_location'),
    path('driver/complete-order/', views.complete_order, name='complete_order'),
    path('driver/order-details/<uuid:order_id>/', views.get_order_details, name='get_order_details'),


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

 path('api/medicines/', views.get_medicines, name='get-medicines'),
    path('api/wallet/', views.get_wallet, name='get_wallet'),
    
    # Money operation endpoints
    path('api/wallet/add/', views.add_money, name='add_money'),
    path('api/wallet/withdraw/', views.withdraw_money, name='withdraw_money'),
    path('api/wallet/operations/', views.get_operations, name='get_operations'),
    path('api/wallet/operations/<int:operation_id>/', views.get_operation_detail, name='operation_detail'),
    path('api/wallet/operations/<int:operation_id>/cancel/', views.cancel_operation, name='cancel_operation'),
    
     path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', views.RegisterView.as_view(), name='register'),


   path('api/medicines/', views.medicine_list, name='medicine_list1'),
    path('api/medicines/<str:medicine_id>/', views.medicine_detail, name='medicine_detail'),
    
    # Comment endpoints - use str to accept UUID
    path('api/medicines/<str:medicine_id>/comments/', views.medicine_comments1, name='medicine_comments1'),
    path('api/comments/<int:comment_id>/', views.comment_detail, name='comment_detail'),
    path('api/my-comments/', views.user_comments, name='user_comments'),
    path('api/medicines/<str:medicine_id>/comments/stats/', views.medicine_comment_stats, name='comment_stats'),

    # List all addresses for current user or create new address
    path('api/addresses/', views.customer_address_list_create, name='address-list-create'),
    
    # Get, update, or delete a specific address
    path('api/addresses/<uuid:id>/', views.customer_address_detail, name='address-detail'),
    
    # Set an address as default
    path('api/addresses/<uuid:address_id>/set-default/', views.set_default_address, name='address-set-default'),
    ]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)