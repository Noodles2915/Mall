from rest_framework import serializers
from order.models import ShoppingCart, CartItem, Order, OrderItem
from product.models import Product
from django.db import transaction


class CartItemSerializer(serializers.ModelSerializer):
    """购物车项目序列化器"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    product_cover_url = serializers.CharField(source='product.cover_url', read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name', 'product_price', 'product_cover_url', 'quantity', 'subtotal']

    def get_subtotal(self, obj):
        return obj.get_subtotal()


class ShoppingCartSerializer(serializers.ModelSerializer):
    """购物车序列化器"""
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    total_quantity = serializers.SerializerMethodField()

    class Meta:
        model = ShoppingCart
        fields = ['id', 'items', 'total_price', 'total_quantity', 'updated_at']

    def get_total_price(self, obj):
        return obj.get_total_price()

    def get_total_quantity(self, obj):
        return obj.get_total_quantity()


class AddCartItemSerializer(serializers.Serializer):
    """添加购物车项目序列化器"""
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)

    def validate(self, data):
        try:
            Product.objects.get(id=data['product_id'])
        except Product.DoesNotExist:
            raise serializers.ValidationError({'product_id': '商品不存在'})
        return data


class UpdateCartItemSerializer(serializers.Serializer):
    """更新购物车项目序列化器"""
    quantity = serializers.IntegerField(min_value=1)


class OrderItemReadSerializer(serializers.ModelSerializer):
    """订单项目读取序列化器"""
    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'product_price', 'quantity', 'subtotal']


class OrderCreateSerializer(serializers.Serializer):
    """订单创建序列化器"""
    address_id = serializers.IntegerField()
    remarks = serializers.CharField(required=False, allow_blank=True)
    payment_method = serializers.ChoiceField(
        choices=['online', 'offline'],
        default='online'
    )

    def validate(self, data):
        from user.models import Address
        try:
            address = Address.objects.get(id=data['address_id'])
        except Address.DoesNotExist:
            raise serializers.ValidationError({'address_id': '地址不存在'})
        data['address'] = address
        return data


class OrderSerializer(serializers.ModelSerializer):
    """订单序列化器"""
    items = OrderItemReadSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'status_display',
            'address_name', 'address_phone', 'address_province', 'address_city', 
            'address_district', 'address_detail', 'remarks', 'total_price', 
            'payment_method', 'items', 'created_at', 'paid_at', 'shipped_at', 
            'received_at', 'cancelled_at'
        ]
        read_only_fields = [
            'id', 'order_number', 'status', 'status_display', 
            'items', 'created_at', 'paid_at', 'shipped_at', 'received_at', 'cancelled_at'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        merchant_user = self.context.get('merchant_user')
        if merchant_user:
            item_queryset = instance.items.filter(product__merchant=merchant_user)
            data['items'] = OrderItemReadSerializer(item_queryset, many=True).data
        return data


class OrderPaySerializer(serializers.Serializer):
    """订单支付序列化器"""
    pass  # 简单的支付操作，无需额外参数


class OrderListSerializer(serializers.ModelSerializer):
    """订单列表序列化器"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    items_count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'order_number', 'status', 'status_display', 'total_price', 'items_count', 'created_at']

    def get_items_count(self, obj):
        merchant_user = self.context.get('merchant_user')
        if merchant_user:
            return obj.items.filter(product__merchant=merchant_user).count()
        return obj.items.count()
