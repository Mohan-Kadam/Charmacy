# orders/urls.py
from django.urls import path
from .views import create_order, approve_order,partial_update_order_item,add_order_item,delete_order_item

urlpatterns = [
    path('orders/', create_order, name='create-order'),
    path('order-item/add/<int:order_id>/', add_order_item, name='add_order_item'),
    path('order-item/partial-update/<int:item_id>/', partial_update_order_item, name='partial_update_order_item'),
    path('order-item/delete/<int:item_id>/', delete_order_item, name='delete_order_item'),
    path('approve/', approve_order, name='approve-order'),

]
