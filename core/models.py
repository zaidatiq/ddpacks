from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

class SKU(models.Model):
    UNIT_CHOICES = [
        ('ml', 'Milliliters'),
        ('g', 'Grams'),
        ('kg', 'Kilograms'),
        ('pcs', 'Pieces'),
        ('litre', 'Litres'),
    ]
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    unit_of_measurement = models.CharField(max_length=20, choices=UNIT_CHOICES)
    units_per_packet = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.CharField(max_length=50)
    main_image = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def clean(self):
        required_fields = [self.code, self.name, self.description,
                           self.unit_of_measurement, self.units_per_packet,
                           self.price, self.capacity]
        if not all(required_fields):
            raise ValidationError("All SKU fields must be filled out.")

    @property
    def case_config(self):
        return f"{self.units_per_packet} x {self.unit_of_measurement}"

    def __str__(self):
        return self.name


class SKUAttribute(models.Model):
    sku = models.ForeignKey(SKU, related_name='attributes', on_delete=models.CASCADE)
    key = models.CharField(max_length=100)
    value = models.TextField()

    def __str__(self):
        return f"{self.sku.code} - {self.key}: {self.value}"


class Inventory(models.Model):
    sku = models.ForeignKey(SKU, on_delete=models.CASCADE)
    total = models.IntegerField()
    available = models.IntegerField()
    reserved = models.IntegerField()

    def clean(self):
        if self.available + self.reserved > self.total:
            raise ValidationError("Available + Reserved cannot exceed Total.")

    def __str__(self):
        return f"{self.sku.code} Inventory"
