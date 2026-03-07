from django.contrib import admin
from order.models import ShoppingCart, CartItem, Order, OrderItem


class CartItemInline(admin.TabularInline):
    """购物车项目内联编辑"""
    model = CartItem
    extra = 0
    readonly_fields = ('created_at', 'updated_at')
    fields = ('product', 'quantity', 'created_at', 'updated_at')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'get_total_quantity', 'get_total_price', 'updated_at')
    list_filter = ('updated_at',)
    search_fields = ('user__username',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'shopping_cart', 'product', 'quantity', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('product__name', 'shopping_cart__user__username')
    readonly_fields = ('created_at', 'updated_at')


class OrderItemInline(admin.TabularInline):
    """订单项目内联编辑"""
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'product_price', 'subtotal')
    fields = ('product', 'product_name', 'product_price', 'quantity', 'subtotal')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'status', 'total_price', 'payment_method', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('order_number', 'user__username', 'address_name')
    readonly_fields = ('order_number', 'created_at', 'paid_at', 'shipped_at', 'received_at', 'cancelled_at')
    fieldsets = (
        ('订单基本信息', {
            'fields': ('order_number', 'user', 'status', 'created_at', 'total_price', 'payment_method', 'remarks')
        }),
        ('收货地址', {
            'fields': ('address_name', 'address_phone', 'address_province', 'address_city', 'address_district', 'address_detail')
        }),
        ('状态时间戳', {
            'fields': ('paid_at', 'shipped_at', 'received_at', 'cancelled_at')
        })
    )
    inlines = [OrderItemInline]
    actions = ['ship_order', 'cancel_order']

    def ship_order(self, request, queryset):
        """发货操作"""
        updated = 0
        for order in queryset:
            if order.can_ship():
                try:
                    order.ship()
                    updated += 1
                except ValueError as e:
                    self.message_user(request, f'{order.order_number}: {str(e)}', level='error')
        self.message_user(request, f'成功发货 {updated} 个订单')

    ship_order.short_description = '发货'

    def cancel_order(self, request, queryset):
        """取消订单操作"""
        updated = 0
        for order in queryset:
            if order.can_cancel():
                try:
                    order.cancel()
                    # 恢复库存
                    for order_item in order.items.all():
                        product = order_item.product
                        product.stock += order_item.quantity
                        product.sales -= order_item.quantity
                        product.save()
                    updated += 1
                except ValueError as e:
                    self.message_user(request, f'{order.order_number}: {str(e)}', level='error')
        self.message_user(request, f'成功取消 {updated} 个订单')

    cancel_order.short_description = '取消訂單'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product_name', 'product_price', 'quantity', 'subtotal')
    list_filter = ('order__created_at',)
    search_fields = ('product_name', 'order__order_number')
