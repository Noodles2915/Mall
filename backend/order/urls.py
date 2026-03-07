from django.urls import path
from rest_framework.routers import DefaultRouter
from order.views import CartViewSet, OrderViewSet, AdminOrderViewSet

app_name = 'order'

urlpatterns = [
    # 购物车相关
    path('cart/', CartViewSet.as_view({'get': 'retrieve_cart'}), name='cart-retrieve'),
    path('cart/add/', CartViewSet.as_view({'post': 'add_item'}), name='cart-add'),
    path('cart/items/<int:item_id>/', CartViewSet.as_view({'put': 'update_item', 'delete': 'remove_item'}), name='cart-update-remove'),
    path('cart/clear/', CartViewSet.as_view({'delete': 'clear'}), name='cart-clear'),

    # 订单相关
    path('orders/', OrderViewSet.as_view({'get': 'list'}), name='order-list'),
    path('orders/<int:order_id>/', OrderViewSet.as_view({'get': 'retrieve'}), name='order-retrieve'),
    path('orders/create/', OrderViewSet.as_view({'post': 'create_order'}), name='order-create'),
    path('orders/<int:order_id>/pay/', OrderViewSet.as_view({'post': 'pay'}), name='order-pay'),
    path('orders/<int:order_id>/cancel/', OrderViewSet.as_view({'post': 'cancel_order'}), name='order-cancel'),
    path('orders/<int:order_id>/receive/', OrderViewSet.as_view({'post': 'receive_order'}), name='order-receive'),

    # 管理员相关
    path('admin/orders/', AdminOrderViewSet.as_view({'get': 'list'}), name='admin-order-list'),
    path('admin/orders/<int:order_id>/ship/', AdminOrderViewSet.as_view({'post': 'ship'}), name='admin-order-ship'),
]
