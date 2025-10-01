from django.contrib import admin
from .models import Product, Order, OrderItem

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("sku", "item_name", "mrp")
    search_fields = ("sku", "item_name")
    list_filter = ("mrp",)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_id", "asm", "created_at", "status")
    list_filter = ("status", "created_at")
    search_fields = ("asm__username",)
    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity", "total")
    list_filter = ("order", "product")
