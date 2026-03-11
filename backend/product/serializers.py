from rest_framework import serializers

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
