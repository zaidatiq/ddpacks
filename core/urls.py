from django.urls import path
from .views import (
    sku_list, sku_detail,
    attribute_list, attribute_detail,
    inventory_list, inventory_detail
)

urlpatterns = [
    #  GET all SKUs, or POST a new SKU
    path('api/skus/', sku_list),

    #  GET/UPDATE/DELETE a single SKU by ID
    path('api/skus/<int:sku_id>/', sku_detail),

    #  POST a new SKU attribute
    path('api/attributes/', attribute_list),

    #  UPDATE/DELETE an attribute by ID
    path('api/attributes/<int:attr_id>/', attribute_detail),

    #  GET all inventory data, or POST new inventory entry
    path('api/inventory/', inventory_list),

    # UPDATE/DELETE inventory by ID
    path('api/inventory/<int:inv_id>/', inventory_detail),
]
