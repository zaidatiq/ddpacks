from rest_framework import serializers
from .models import SUKMaster, Inventory

class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = '__all__'

class SUKMasterSerializer(serializers.ModelSerializer):
    inventory = InventorySerializer(read_only=True)

    class Meta:
        model = SUKMaster
        fields = '__all__'
