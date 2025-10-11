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
            'date': openapi.Schema(type=openapi.TYPE_STRING, description='red'),

            'items': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'sku': openapi.Schema(type=openapi.TYPE_STRING, description='Product ID from master'),
                        'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description='Quantity ordered'),
                        'tester_quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description='Testing Quantity'),

                    },
                    required=['sku', 'quantity', 'tester_quantity'],
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
    date = request.data.get('date')
    print('date---', date)
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
            date=date,
            product=product,
            quantity=item['quantity'],
            total=total,
            tester_quantity=item['tester_quantity']
        )

        response_items.append({
            'sku': product.sku,
            'item_name': product.item_name,
            'mrp': float(product.mrp),
            'quantity': item['quantity'],
            'tester_quantity': item['tester_quantity'],
            'total': total
        })


    return Response({
        'order_id': order.order_id,
        'date':date,
        'items': response_items
    }, status=status.HTTP_201_CREATED)

from .models import Order, OrderItem
from .serializers import OrderApprovalSerializer, OrderItemSerializer

@swagger_auto_schema(
    method='GET',
    responses={
        200: openapi.Response('Orders list', examples={
            'application/json': [
                {'order_id': 1, 'status': 'PENDING'},
                {'order_id': 2, 'status': 'APPROVED'}
            ]
        })
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pending_orders(request):
    """List all orders with PENDING status"""
    orders = Order.objects.filter(status='PENDING')
    data = [{'order_id': o.id, 'status': o.status} for o in orders]
    return Response(data)


@swagger_auto_schema(
    method='post',
    operation_description="Approve or reject an order with markup margins. \
    SCM acts first (can approve/reject with markup details). \
    Once SCM approves, MSR can then approve/reject.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['order_id', 'status'],
        properties={
            'order_id': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description='ID of the order to approve/reject'
            ),
            'status': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='New status: SCM_APPROVED / SCM_REJECTED / MSR_APPROVED / MSR_REJECTED'
            ),
            'markup_margin': openapi.Schema(
                type=openapi.TYPE_NUMBER,
                format='float',
                description='Overall markup margin percentage for the order (e.g., 23%)',
                default=0.00
            ),
            'distributorship_markup_margin': openapi.Schema(
                type=openapi.TYPE_NUMBER,
                format='float',
                description='Distributorship markup margin percentage (e.g., 8%)',
                default=0.00
            ),
            'advance_payment_markup_margin': openapi.Schema(
                type=openapi.TYPE_NUMBER,
                format='float',
                description='Advance payment markup margin percentage (e.g., 1%)',
                default=0.00
            ),
            'sales_target_markup_margin': openapi.Schema(
                type=openapi.TYPE_NUMBER,
                format='float',
                description='Sales target markup margin percentage (e.g., 1%)',
                default=0.00
            ),
        },
        example={
            "order_id": 3,
            "status": "SCM_APPROVED",
            "markup_margin": 400,
            "distributorship_markup_margin": 300,
            "advance_payment_markup_margin": 100,
            "sales_target_markup_margin": 50
        }
    ),
    responses={
        200: openapi.Response(
            description='Order approved/rejected successfully',
            examples={
                'application/json': {
                    'order_id': 3,
                    'status': 'SCM_APPROVED',
                    'scm_approver': 'scm_user',
                    'msr_approver': None,
                    'markup_margin': 23.0,
                    'distributorship_markup_margin': 8.0,
                    'advance_payment_markup_margin': 1.0,
                    'sales_target_markup_margin': 1.0
                }
            }
        ),
        400: openapi.Response(description='Bad Request (Invalid status or duplicate approval)'),
        404: openapi.Response(description='Order Not Found'),
    }
)

@api_view(['POST'])
@permission_classes([IsAuthenticated])

def approve_order(request):
    """
    Approve or reject an order with markup margins.
    First SCM approves/rejects.
    Then MSR approves/rejects.
    """
    serializer = OrderApprovalSerializer(data=request.data)
    if serializer.is_valid():
        order_id = serializer.validated_data['order_id']
        new_status = serializer.validated_data['status']

        try:
            order = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        user = request.user

        # Extract margin values if present
        markup_margin = serializer.validated_data.get('markup_margin')
        distributorship_markup = serializer.validated_data.get('distributorship_markup_margin')
        advance_payment_markup = serializer.validated_data.get('advance_payment_markup_margin')
        sales_target_markup = serializer.validated_data.get('sales_target_markup_margin')

        # SCM approval
        if new_status in ['SCM_APPROVED', 'SCM_REJECTED']:
            if order.status != 'Pending':
                return Response({'error': 'Order already SCM reviewed'}, status=status.HTTP_400_BAD_REQUEST)

            order.status = new_status
            order.scm_approver = user

            # Save markups (even if some are None)
            order.markup_margin = markup_margin
            order.distributorship_markup_margin = distributorship_markup
            order.advance_payment_markup_margin = advance_payment_markup
            order.sales_target_markup_margin = sales_target_markup

            order.save()
        
        # MSR approval
        elif new_status in ['MSR_APPROVED', 'MSR_REJECTED']:
            if order.status != 'SCM_APPROVED':
                return Response({'error': 'Order not approved by SCM yet'}, status=status.HTTP_400_BAD_REQUEST)

            order.status = new_status
            order.msr_approver = user
            order.save()

        return Response({
            'order_id': order.order_id,
            'status': order.status,
            'scm_approver': order.scm_approver.username if order.scm_approver else None,
            'msr_approver': order.msr_approver.username if order.msr_approver else None,
            'markup_margin': order.markup_margin,
            'distributorship_markup_margin': order.distributorship_markup_margin,
            'advance_payment_markup_margin': order.advance_payment_markup_margin,
            'sales_target_markup_margin': order.sales_target_markup_margin
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@swagger_auto_schema(
    method='post',
    operation_description="Add a new item under an existing order. The date will automatically be inherited from the parent order.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['sku', 'quantity'],
        properties={
            'sku': openapi.Schema(
                type=openapi.TYPE_STRING,
                description='SKU of the product to add'
            ),
            'quantity': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description='Quantity of the product'
            ),
            'tester_quantity': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description='Tester quantity (optional)',
                default=0
            ),
        },
        example={
            "sku": "PROD123",
            "quantity": 10,
            "tester_quantity": 1
        }
    ),
    responses={
        201: openapi.Response(
            description="New item added successfully",
            examples={
                "application/json": {
                    "message": "New item added successfully",
                    "order_id": 12,
                    "order_date": "2025-10-09",
                    "item": {
                        "id": 101,
                        "sku": "PROD123",
                        "item_name": "Product Name",
                        "mrp": 250.0,
                        "quantity": 10,
                        "tester_quantity": 1,
                        "total": 2500.0
                    }
                }
            }
        ),
        400: openapi.Response(description="Invalid data or product not found"),
        404: openapi.Response(description="Order not found")
    }
)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_order_item(request, order_id):
    """Add a new item under an existing order"""
    try:
        order = Order.objects.get(order_id=order_id)
        orderitem = OrderItem.objects.filter(order_id=order_id).first()

    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    product_sku = request.data.get('sku')
    quantity = request.data.get('quantity', 0)
    tester_quantity = request.data.get('tester_quantity', 0)

    # Validate product
    try:
        product = Product.objects.get(sku=product_sku)  
    except Product.DoesNotExist:
        return Response({'error': f"Product with SKU {product_sku} not found"}, status=status.HTTP_400_BAD_REQUEST)

    # Compute total
    total = product.mrp * int(quantity)
    order_date = orderitem.date
    
    # Create the new order item
    order_item = OrderItem.objects.create(
        order=order,
        product=product,
        quantity=quantity,
        tester_quantity=tester_quantity,
        total=total,
        mrp=product.mrp,
        date=order_date
    )

    serializer = OrderItemSerializer(order_item)

    return Response({
        'message': 'New item added successfully',
        'order_id': order.order_id,
        'item': serializer.data
    }, status=status.HTTP_201_CREATED)





@swagger_auto_schema(
    method='patch',
    request_body=OrderItemSerializer,
    responses={
        200: openapi.Response('Order item partially updated successfully'),
        404: 'Item not found'
    }
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def partial_update_order_item(request, item_id):
    """Partially update specific fields of an OrderItem (like tester_quantity)"""
    try:
        item = OrderItem.objects.get(id=item_id)
    except OrderItem.DoesNotExist:
        return Response({'error': 'Order item not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = OrderItemSerializer(item, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Order item partially updated successfully', 'data': serializer.data})
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@swagger_auto_schema(
    method='delete',
    manual_parameters=[
        openapi.Parameter('item_id', openapi.IN_PATH, description="ID of the order item to delete", type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: openapi.Response('Order item deleted successfully'),
        404: 'Item not found'
    }
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_order_item(request, item_id):
    """Delete a specific OrderItem"""
    try:
        item = OrderItem.objects.get(id=item_id)
        item.delete()
        return Response({'message': 'Order item deleted successfully'}, status=status.HTTP_200_OK)
    except OrderItem.DoesNotExist:
        return Response({'error': 'Order item not found'}, status=status.HTTP_404_NOT_FOUND)
