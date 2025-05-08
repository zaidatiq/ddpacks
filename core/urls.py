from django.urls import path
from .views import my_name_view

urlpatterns = [
    path('', my_name_view),
]
