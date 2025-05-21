from django.urls import path
from . import views
from .views import sku_manage, sku_detail_combined,inventory_detail, inventory_list
from .views import admin_register_view,sku_list
urlpatterns = [
    # Public endpoints
    path('api/register/', views.register_view, name='register'),
    path('api/activate/<str:uidb64>/<str:token>/', views.activate_account, name='activate'),
    path('api/login/', views.login_view, name='login'),
    path('api/request-password-reset/', views.request_password_reset, name='request-password-reset'),
    path('api/reset-password/<str:uidb64>/<str:token>/', views.reset_password, name='reset-password'),
    path('api/skus/', sku_list, name='sku_list'),
    # SKU endpoints (admin required for manage)
    path('api/skus/', views.sku_detail_combined, name='sku-list'),  # GET all SKUs or details (if modified)
    path('api/sku/<int:sku_id>/', views.sku_detail_combined, name='sku-detail-combined'),
    path('api/admin/sku/', views.sku_manage, name='sku-create'),
    path('api/admin/sku/<int:sku_id>/', views.sku_manage, name='sku-manage'),

    # Inventory endpoints (admin only)
    path('api/inventory/', views.inventory_list, name='inventory-list'),
    path('api/inventory/<int:inv_id>/', views.inventory_detail, name='inventory-detail'),

    # Cart endpoints (authenticated users only)
    path('api/cart/add/', views.add_to_cart, name='add-to-cart'),
    path('api/cart/view/', views.view_cart, name='view-cart'),
    path('api/cart/remove/', views.remove_from_cart, name='remove-from-cart'),

    # Protected example
    path('api/protected/', views.protected_view, name='protected'),
]



