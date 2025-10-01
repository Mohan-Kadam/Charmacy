from django.db import models

class Product(models.Model):
    sku = models.CharField(max_length=50, unique=True)
    item_name = models.CharField(max_length=100)
    mrp = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.item_name} ({self.sku})"
