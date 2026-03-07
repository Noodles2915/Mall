from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils import timezone
from datetime import datetime
import uuid

from order.models import ShoppingCart, CartItem, Order, OrderItem
from order.serializers import (
    ShoppingCartSerializer, CartItemSerializer, AddCartItemSerializer,
    UpdateCartItemSerializer, OrderSerializer, OrderCreateSerializer,
    OrderPaySerializer, OrderListSerializer
)
from product.models import Product
from user.models import Address


class CartViewSet(viewsets.ViewSet):
    """购物车视图集"""
    permission_classes = [IsAuthenticated]

    def get_or_create_cart(self, user):
        """获取或创建购物车"""
        cart, created = ShoppingCart.objects.get_or_create(user=user)
        return cart

    @action(detail=False, methods=['get'])
    def retrieve_cart(self, request):
        """获取购物车"""
        cart = self.get_or_create_cart(request.user)
        serializer = ShoppingCartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """添加商品到购物车"""
        serializer = AddCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart = self.get_or_create_cart(request.user)
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']

        product = Product.objects.get(id=product_id)

        # 检查库存
        if product.stock < quantity:
            return Response(
                {'error': '库存不足'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 如果商品已在购物车中，增加数量
        cart_item, created = CartItem.objects.get_or_create(
            shopping_cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            if cart_item.product.stock < cart_item.quantity:
                return Response(
                    {'error': '库存不足'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            cart_item.save()

        cart.save()  # 更新购物车更新时间
        cart_serializer = ShoppingCartSerializer(cart)
        return Response(cart_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['put'], url_path=r'items/(?P<item_id>\d+)')
    def update_item(self, request, item_id=None):
        """更新购物车项目数量"""
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            cart_item = CartItem.objects.get(id=item_id, shopping_cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response(
                {'error': '购物车项目不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

        # 检查库存
        if cart_item.product.stock < serializer.validated_data['quantity']:
            return Response(
                {'error': '库存不足'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_item.quantity = serializer.validated_data['quantity']
        cart_item.save()
        cart_item.shopping_cart.save()

        cart_serializer = ShoppingCartSerializer(cart_item.shopping_cart)
        return Response(cart_serializer.data)

    @action(detail=False, methods=['delete'], url_path=r'items/(?P<item_id>\d+)')
    def remove_item(self, request, item_id=None):
        """删除购物车项目"""
        try:
            cart_item = CartItem.objects.get(id=item_id, shopping_cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response(
                {'error': '购物车项目不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

        cart = cart_item.shopping_cart
        cart_item.delete()
        cart.save()

        cart_serializer = ShoppingCartSerializer(cart)
        return Response(cart_serializer.data)

    @action(detail=False, methods=['delete'])
    def clear(self, request):
        """清空购物车"""
        try:
            cart = ShoppingCart.objects.get(user=request.user)
            cart.items.all().delete()
            cart.save()
        except ShoppingCart.DoesNotExist:
            pass

        cart = self.get_or_create_cart(request.user)
        serializer = ShoppingCartSerializer(cart)
        return Response(serializer.data)


class OrderViewSet(viewsets.ViewSet):
    """订单视图集"""
    permission_classes = [IsAuthenticated]

    def _generate_order_number(self):
        """生成订单号"""
        return 'ORD' + datetime.now().strftime('%Y%m%d%H%M%S') + str(uuid.uuid4().hex)[:8].upper()

    @action(detail=False, methods=['get'])
    def list(self, request):
        """订单列表"""
        orders = Order.objects.filter(user=request.user)
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path=r'(?P<order_id>\d+)')
    def retrieve(self, request, order_id=None):
        """获取订单详情"""
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response(
                {'error': '订单不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = OrderSerializer(order)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def create_order(self, request):
        """创建订单"""
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            cart = ShoppingCart.objects.get(user=request.user)
            if not cart.items.exists():
                return Response(
                    {'error': '购物车为空'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except ShoppingCart.DoesNotExist:
            return Response(
                {'error': '购物车为空'},
                status=status.HTTP_400_BAD_REQUEST
            )

        address = serializer.validated_data['address']

        with transaction.atomic():
            # 检查库存并创建订单
            total_price = 0
            for cart_item in cart.items.all():
                if cart_item.product.stock < cart_item.quantity:
                    return Response(
                        {'error': f'商品 {cart_item.product.name} 库存不足'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                total_price += cart_item.get_subtotal()

            # 创建订单
            order = Order.objects.create(
                user=request.user,
                order_number=self._generate_order_number(),
                address_name=address.name,
                address_phone=address.phone,
                address_province=address.province,
                address_city=address.city,
                address_district=address.district,
                address_detail=address.detail,
                remarks=serializer.validated_data.get('remarks', ''),
                total_price=total_price,
                payment_method=serializer.validated_data['payment_method']
            )

            # 创建订单项目并扣除库存
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    product_name=cart_item.product.name,
                    product_price=cart_item.product.price,
                    quantity=cart_item.quantity
                )
                # 扣除库存
                product = cart_item.product
                product.stock -= cart_item.quantity
                product.sales += cart_item.quantity
                product.save()

            # 清空购物车
            cart.items.all().delete()

        order_serializer = OrderSerializer(order)
        return Response(order_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path=r'(?P<order_id>\d+)/pay')
    def pay(self, request, order_id=None):
        """支付订单"""
        serializer = OrderPaySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response(
                {'error': '订单不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

        if not order.can_pay():
            return Response(
                {'error': f'订单状态为 {order.get_status_display()} 时无法支付'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 模拟支付处理
        try:
            order.pay()
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        order_serializer = OrderSerializer(order)
        return Response(order_serializer.data)

    @action(detail=False, methods=['post'], url_path=r'(?P<order_id>\d+)/cancel')
    def cancel_order(self, request, order_id=None):
        """取消订单"""
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response(
                {'error': '订单不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

        if not order.can_cancel():
            return Response(
                {'error': f'订单状态为 {order.get_status_display()} 时无法取消'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            order.cancel()
            # 恢复库存
            for order_item in order.items.all():
                product = order_item.product
                product.stock += order_item.quantity
                product.sales -= order_item.quantity
                product.save()
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        order_serializer = OrderSerializer(order)
        return Response(order_serializer.data)

    @action(detail=False, methods=['post'], url_path=r'(?P<order_id>\d+)/receive')
    def receive_order(self, request, order_id=None):
        """确认收货"""
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response(
                {'error': '订单不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

        if not order.can_receive():
            return Response(
                {'error': f'订单状态为 {order.get_status_display()} 时无法确认收货'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            order.receive()
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        order_serializer = OrderSerializer(order)
        return Response(order_serializer.data)


class AdminOrderViewSet(viewsets.ViewSet):
    """管理员订单视图集"""
    permission_classes = [IsAuthenticated]

    def check_admin_permission(self, request):
        """检查是否是管理员"""
        if not request.user.is_staff:
            return Response(
                {'error': '只有管理员可以访问'},
                status=status.HTTP_403_FORBIDDEN
            )

    @action(detail=False, methods=['get'])
    def list(self, request):
        """获取所有订单列表"""
        admin_check = self.check_admin_permission(request)
        if admin_check:
            return admin_check

        # 支持按状态筛选
        status_filter = request.query_params.get('status')
        if status_filter:
            orders = Order.objects.filter(status=status_filter)
        else:
            orders = Order.objects.all()

        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path=r'(?P<order_id>\d+)/ship')
    def ship(self, request, order_id=None):
        """管理员发货"""
        admin_check = self.check_admin_permission(request)
        if admin_check:
            return admin_check

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response(
                {'error': '订单不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

        if not order.can_ship():
            return Response(
                {'error': f'订单状态为 {order.get_status_display()} 时无法发货'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            order.ship()
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        order_serializer = OrderSerializer(order)
        return Response(order_serializer.data)
