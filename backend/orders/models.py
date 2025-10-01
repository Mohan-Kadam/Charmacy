from django.db import models
from django.conf import settings
from products.models import Product

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    asm = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="Pending")  # Pending / Accepted / Rejected

    def __str__(self):
        return f"Order {self.order_id} by {self.asm.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.product.item_name} (x{self.quantity})"
