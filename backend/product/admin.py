from django.contrib import admin

from .models import HomeBanner, Product, ProductCategory, ProductImage, ServiceMessage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "parent", "is_active", "sort")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "price", "stock", "is_hot", "is_active")
    list_filter = ("is_hot", "is_active", "category")
    search_fields = ("name", "subtitle")
    inlines = [ProductImageInline]


@admin.register(HomeBanner)
class HomeBannerAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "is_active", "sort")
    list_filter = ("is_active",)
    search_fields = ("title",)


@admin.register(ServiceMessage)
class ServiceMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "user", "created_at")
    search_fields = ("product__name", "user__username", "content")
