from django.db import models
from django.conf import settings
from products.models import Product

# class Order(models.Model):

#     STATUS_CHOICES = [
#         ('PENDING', 'Pending'),
#         ('ACCEPTED', 'Accepted'),
#         ('REJECTED', 'Rejected'),
#     ]

#     order_id = models.AutoField(primary_key=True)
#     asm = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)
#     status = models.CharField(max_length=20, default="Pending")  # Pending / Accepted / Rejected


class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SCM_APPROVED', 'SCM Approved'),
        ('SCM_REJECTED', 'SCM Rejected'),
        ('MSR_APPROVED', 'MSR Approved'),
        ('MSR_REJECTED', 'MSR Rejected'),
    ]

    order_id = models.AutoField(primary_key=True)
    asm = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders_created')
    scm_approver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders_scm_approved')
    msr_approver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders_msr_approved')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    # new markup fields
    markup_margin = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    distributorship_markup_margin = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    advance_payment_markup_margin = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    sales_target_markup_margin = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)



    def __str__(self):
        return f"Order {self.order_id} by {self.asm.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total = models.DecimalField(max_digits=12, decimal_places=2)
    tester_quantity = models.IntegerField(default=0)
    mrp = models.DecimalField(max_digits=10, decimal_places=2) 
    date = models.DateField(null=True, blank=True)


    def save(self, *args, **kwargs):
        # Automatically set MRP from the Product table before saving
        if self.product and not self.mrp:
            self.mrp = self.product.mrp

        # Calculate total automatically
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.item_name} (x{self.quantity})"
