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
            "category",
            "category_name",
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)

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
        ]


class ServiceMessageSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = ServiceMessage
        fields = ["id", "product", "username", "content", "reply", "created_at"]
        read_only_fields = ["id", "username", "reply", "created_at", "product"]
