from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import SUKMaster, Inventory
from .serializers import SUKMasterSerializer, InventorySerializer

class SUKMasterViewSet(viewsets.ModelViewSet):
    queryset = SUKMaster.objects.all()
    serializer_class = SUKMasterSerializer

class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
