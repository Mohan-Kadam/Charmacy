from rest_framework import serializers
from .models import  Order, OrderItem
from products.models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'sku', 'item_name', 'mrp']


class OrderItemSerializer(serializers.ModelSerializer):
    # Nested read-only product details
    product = ProductSerializer(read_only=True)

    # Accept product_id from frontend
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_id', 'quantity', 'total', 'tester_quantity']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)  # Nested items
    created_by = serializers.StringRelatedField(read_only=True)  # show username

    class Meta:
        model = Order
        fields = ['id', 'created_by', 'created_at', 'status', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        asm = self.context['request'].user  # logged-in ASM
        order = Order.objects.create(created_by=asm, **validated_data)

        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        return order


class OrderApprovalSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(write_only=True)
    markup_margin = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    distributorship_markup_margin = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    advance_payment_markup_margin = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    sales_target_markup_margin = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)


    class Meta:
        model = Order
        fields = [
            'order_id', 'status',
            'markup_margin', 'distributorship_markup_margin',
            'advance_payment_markup_margin', 'sales_target_markup_margin'
        ]
    def validate_status(self, value):
        if value not in ['SCM_APPROVED', 'SCM_REJECTED', 'MSR_APPROVED', 'MSR_REJECTED']:
            raise serializers.ValidationError("Invalid status for approval")
        return value

