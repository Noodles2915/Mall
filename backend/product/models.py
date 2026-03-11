from django.conf import settings
from django.db import models


class ProductCategory(models.Model):
    name = models.CharField(max_length=50, verbose_name="分类名称")
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="父级分类",
    )
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    sort = models.PositiveIntegerField(default=0, verbose_name="排序")

    class Meta:
        verbose_name = "商品分类"
        verbose_name_plural = "商品分类"
        ordering = ["sort", "id"]

    def __str__(self):
        return self.name


class Product(models.Model):
    merchant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="merchant_products",
        null=True,
        blank=True,
        verbose_name="所属商家",
    )
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="所属分类",
    )
    name = models.CharField(max_length=100, verbose_name="商品名称")
    subtitle = models.CharField(max_length=200, blank=True, default="", verbose_name="副标题")
    cover_url = models.URLField(max_length=500, verbose_name="封面图")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="价格")
    stock = models.PositiveIntegerField(default=0, verbose_name="库存")
    sales = models.PositiveIntegerField(default=0, verbose_name="销量")
    is_hot = models.BooleanField(default=False, verbose_name="热门推荐")
    is_active = models.BooleanField(default=True, verbose_name="是否上架")
    description = models.TextField(blank=True, default="", verbose_name="商品描述")
    specs = models.JSONField(default=dict, blank=True, verbose_name="规格信息")
    customer_service_hint = models.CharField(
        max_length=200,
        blank=True,
        default="联系客服获取更多详情",
        verbose_name="客服提示",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "商品"
        verbose_name_plural = "商品"
        ordering = ["-is_hot", "-sales", "-id"]

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="商品",
    )
    image_url = models.URLField(max_length=500, verbose_name="图片地址")
    sort = models.PositiveIntegerField(default=0, verbose_name="排序")

    class Meta:
        verbose_name = "商品图片"
        verbose_name_plural = "商品图片"
        ordering = ["sort", "id"]

    def __str__(self):
        return f"{self.product.name}-图片{self.pk}"


class HomeBanner(models.Model):
    title = models.CharField(max_length=100, verbose_name="标题")
    image_url = models.URLField(max_length=500, verbose_name="轮播图")
    link = models.CharField(max_length=255, blank=True, default="", verbose_name="跳转链接")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    sort = models.PositiveIntegerField(default=0, verbose_name="排序")

    class Meta:
        verbose_name = "首页轮播"
        verbose_name_plural = "首页轮播"
        ordering = ["sort", "id"]

    def __str__(self):
        return self.title


class ServiceMessage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="service_messages",
        verbose_name="商品",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="service_messages",
        verbose_name="用户",
    )
    content = models.TextField(verbose_name="留言内容")
    reply = models.TextField(blank=True, default="", verbose_name="客服回复")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "客服留言"
        verbose_name_plural = "客服留言"
        ordering = ["-id"]

    def __str__(self):
        return f"{self.user.username}-{self.product.name}"
