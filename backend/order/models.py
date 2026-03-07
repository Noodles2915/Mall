from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator
from product.models import Product


class ShoppingCart(models.Model):
    """购物车模型"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='用户'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '购物车'
        verbose_name_plural = '购物车'

    def __str__(self):
        return f'{self.user.username}的购物车'

    def get_total_price(self):
        """计算购物车总价"""
        return sum(item.get_subtotal() for item in self.items.all())

    def get_total_quantity(self):
        """获取购物车商品总数"""
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    """购物车项目"""
    shopping_cart = models.ForeignKey(
        ShoppingCart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='购物车'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='商品',
        related_name='cart_items'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='数量'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '购物车项目'
        verbose_name_plural = '购物车项目'
        unique_together = ('shopping_cart', 'product')

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'

    def get_subtotal(self):
        """计算小计"""
        return self.product.price * self.quantity


class Order(models.Model):
    """订单模型"""
    ORDER_STATUS_CHOICES = [
        ('pending_payment', '待支付'),
        ('pending_delivery', '待发货'),
        ('pending_receipt', '待收货'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name='用户'
    )
    order_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='订单号'
    )
    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default='pending_payment',
        verbose_name='订单状态'
    )
    # 收货地址信息（保存快照以防地址被删除）
    address_name = models.CharField(max_length=50, verbose_name='收货人姓名')
    address_phone = models.CharField(max_length=20, verbose_name='联系电话')
    address_province = models.CharField(max_length=20, verbose_name='省份')
    address_city = models.CharField(max_length=20, verbose_name='城市')
    address_district = models.CharField(max_length=20, verbose_name='区县')
    address_detail = models.CharField(max_length=100, verbose_name='详细地址')

    remarks = models.TextField(blank=True, default='', verbose_name='备注')
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='订单总价'
    )
    payment_method = models.CharField(
        max_length=20,
        default='online',
        verbose_name='支付方式',
        help_text='online:在线支付, offline:线下支付'
    )

    # 状态时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name='支付时间')
    shipped_at = models.DateTimeField(null=True, blank=True, verbose_name='发货时间')
    received_at = models.DateTimeField(null=True, blank=True, verbose_name='收货时间')
    cancelled_at = models.DateTimeField(null=True, blank=True, verbose_name='取消时间')

    class Meta:
        verbose_name = '订单'
        verbose_name_plural = '订单'
        ordering = ['-created_at']

    def __str__(self):
        return f'订单 {self.order_number}'

    def can_pay(self):
        """判断是否可以支付"""
        return self.status == 'pending_payment'

    def can_ship(self):
        """判断是否可以发货"""
        return self.status == 'pending_delivery'

    def can_receive(self):
        """判断是否可以收货"""
        return self.status == 'pending_receipt'

    def can_cancel(self):
        """判断是否可以取消"""
        return self.status in ['pending_payment', 'pending_delivery']

    def pay(self):
        """支付订单"""
        if not self.can_pay():
            raise ValueError(f'订单状态为 {self.get_status_display()} 时无法支付')
        self.status = 'pending_delivery'
        from django.utils import timezone
        self.paid_at = timezone.now()
        self.save()

    def ship(self):
        """发货"""
        if not self.can_ship():
            raise ValueError(f'订单状态为 {self.get_status_display()} 时无法发货')
        self.status = 'pending_receipt'
        from django.utils import timezone
        self.shipped_at = timezone.now()
        self.save()

    def receive(self):
        """确认收货"""
        if not self.can_receive():
            raise ValueError(f'订单状态为 {self.get_status_display()} 时无法确认收货')
        self.status = 'completed'
        from django.utils import timezone
        self.received_at = timezone.now()
        self.save()

    def cancel(self):
        """取消订单"""
        if not self.can_cancel():
            raise ValueError(f'订单状态为 {self.get_status_display()} 时无法取消')
        self.status = 'cancelled'
        from django.utils import timezone
        self.cancelled_at = timezone.now()
        self.save()


class OrderItem(models.Model):
    """订单项目"""
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='订单'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='商品'
    )
    product_name = models.CharField(max_length=100, verbose_name='商品名称')
    product_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='商品价格'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='数量'
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='小计'
    )

    class Meta:
        verbose_name = '订单项目'
        verbose_name_plural = '订单项目'

    def __str__(self):
        return f'{self.product_name} x {self.quantity}'

    def save(self, *args, **kwargs):
        if not self.product_name:
            self.product_name = self.product.name
        if not self.product_price:
            self.product_price = self.product.price
        self.subtotal = self.product_price * self.quantity
        super().save(*args, **kwargs)
