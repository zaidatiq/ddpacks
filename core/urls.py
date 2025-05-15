from django.urls import path
from . import views

urlpatterns = [
    path('api/register/', views.register_view),
    path('api/login/', views.login_view),
    path('api/protected/', views.protected_view),
    path('api/skus/', views.sku_list),
    path('api/skus/<int:sku_id>/', views.sku_detail),
    path('api/attributes/', views.attribute_list),
    path('api/attributes/<int:attr_id>/', views.attribute_detail),
    path('api/inventory/', views.inventory_list),
    path('api/inventory/<int:inv_id>/', views.inventory_detail),
]
