from rest_framework import serializers
from urllib.parse import urlparse

from .models import HomeBanner, Product, ProductCategory, ProductImage, ServiceMessage


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ["id", "name", "parent", "sort"]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image_url", "sort"]


class HomeBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeBanner
        fields = ["id", "title", "image_url", "link", "sort"]


class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    merchant_id = serializers.IntegerField(source="merchant.id", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "subtitle",
            "cover_url",
            "price",
            "stock",
            "sales",
            "is_hot",
            "is_active",
            "category",
            "category_name",
            "merchant_id",
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    merchant_id = serializers.IntegerField(source="merchant.id", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "subtitle",
            "cover_url",
            "price",
            "stock",
            "sales",
            "is_hot",
            "description",
            "specs",
            "customer_service_hint",
            "category",
            "images",
            "is_active",
            "merchant_id",
        ]


class MerchantProductCreateUpdateSerializer(serializers.ModelSerializer):
    cover_url = serializers.CharField(max_length=500, trim_whitespace=True)

    class Meta:
        model = Product
        fields = [
            "category",
            "name",
            "subtitle",
            "cover_url",
            "price",
            "stock",
            "is_hot",
            "is_active",
            "description",
            "specs",
            "customer_service_hint",
        ]

    def validate_cover_url(self, value):
        normalized = (
            value.strip()
            .replace("：", ":")
            .replace("／", "/")
            .replace("。", ".")
        )
        if not normalized:
            raise serializers.ValidationError("封面图 URL 不能为空")

        if normalized.startswith("//"):
            normalized = f"https:{normalized}"
        elif not normalized.lower().startswith(("http://", "https://")):
            normalized = f"https://{normalized}"

        parsed = urlparse(normalized)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise serializers.ValidationError("请输入有效的 http/https 图片地址")

        return normalized


class MerchantProductDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "category",
            "category_name",
            "name",
            "subtitle",
            "cover_url",
            "price",
            "stock",
            "sales",
            "is_hot",
            "is_active",
            "description",
            "specs",
            "customer_service_hint",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "sales", "created_at", "updated_at"]


class ServiceMessageSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = ServiceMessage
        fields = ["id", "product", "username", "content", "reply", "created_at"]
        read_only_fields = ["id", "username", "reply", "created_at", "product"]


class ServiceMessageAdminSerializer(serializers.ModelSerializer):
    """管理员/商家获取客服留言的序列化器"""
    username = serializers.CharField(source="user.username", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    user_id = serializers.IntegerField(source="user.id", read_only=True)

    class Meta:
        model = ServiceMessage
        fields = ["id", "product", "product_name", "user_id", "username", "content", "reply", "created_at"]
        read_only_fields = ["id", "product", "product_name", "user_id", "username", "content", "created_at"]


class ServiceMessageAdminReplySerializer(serializers.Serializer):
    """管理员/商家回复客服留言的序列化器"""
    reply = serializers.CharField(max_length=1000, min_length=1)
