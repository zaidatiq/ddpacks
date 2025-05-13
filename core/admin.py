from django.contrib import admin

# Register your models here.

from .models import SKU, SKUAttribute, Inventory

admin.site.register(SKU)
admin.site.register(SKUAttribute)
admin.site.register(Inventory)

