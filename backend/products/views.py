from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import api_view

from .models import Product


@swagger_auto_schema(
    method='get',
    responses={
        200: openapi.Response(
            description="List of products from master",
            examples={
                "application/json": [
                    {"sku": "SKU123", "item_name": "Paracetamol", "mrp": 50.0},
                    {"sku": "SKU124", "item_name": "Ibuprofen", "mrp": 80.0},
                ]
            },
        )
    }
)
@api_view(['GET'])
def get_products(request):
    products = Product.objects.all()
    product_list = [
        {"sku": p.sku, "item_name": p.item_name, "mrp": float(p.mrp)}
        for p in products
    ]
    return JsonResponse(product_list, safe=False)
