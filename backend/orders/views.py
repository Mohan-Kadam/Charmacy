from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Order, OrderItem, Product
from .serializers import OrderSerializer


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['items'],
        properties={
            'items': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'sku': openapi.Schema(type=openapi.TYPE_STRING, description='Product ID from master'),
                        'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description='Quantity ordered'),
                    },
                    required=['sku', 'quantity'],
                ),
            ),
        },
    ),
    responses={
        201: openapi.Response('Order Created Successfully', examples={
            'application/json': {
                'order_id': 1,
                'items': [
                    {'sku': 1, 'item_name': 'Paracetamol', 'mrp': 50.0, 'quantity': 2, 'total': 100.0},
                    {'sku': 3, 'item_name': 'Ibuprofen', 'mrp': 80.0, 'quantity': 1, 'total': 80.0}
                ]
            }
        }),
        400: 'Bad Request'
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    """Create an order for the logged-in ASM"""
    asm = request.user  # Automatically use logged-in user

    items_data = request.data.get('items', [])
    if not items_data:
        return Response({'error': 'No items provided'}, status=status.HTTP_400_BAD_REQUEST)

    order = Order.objects.create(asm=asm)  # Create order linked to ASM

    response_items = []
    for item in items_data:
        print("item", item)
        try:
            product = Product.objects.get(sku=item['sku'])
        except Product.DoesNotExist:
            return Response({'error': f"Product ID {item['sku']} does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        total = product.mrp * item['quantity']

        order_item = OrderItem.objects.create(
            order=order,
            product=product,
            quantity=item['quantity'],
            total=total
        )

        response_items.append({
            'sku': product.sku,
            'item_name': product.item_name,
            'mrp': float(product.mrp),
            'quantity': item['quantity'],
            'total': total
        })

    return Response({
        'order_id': order.order_id,
        'items': response_items
    }, status=status.HTTP_201_CREATED)
