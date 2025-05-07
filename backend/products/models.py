from django.db import models

# Create your models here.

class SUKMaster(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    case_config = models.CharField(max_length=100, blank=True)
    unit_of_measurement = models.CharField(max_length=50)
    units_per_packet = models.PositiveIntegerField()

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

class Inventory(models.Model):
    suk = models.OneToOneField(SUKMaster, on_delete=models.CASCADE, related_name='inventory')
    quantity = models.PositiveIntegerField(default=0)
    available = models.PositiveIntegerField(default=0)
    reserved = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Inventory for {self.suk.code}"
