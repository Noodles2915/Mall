from django.contrib import admin

from .models import HomeBanner, Product, ProductCategory, ProductImage, ServiceMessage


def is_admin_or_superuser(user):
    return user.is_superuser or getattr(user, "is_admin_role", False)


def is_merchant(user):
    return getattr(user, "is_merchant_role", False)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "parent", "is_active", "sort")
    list_filter = ("is_active",)
    search_fields = ("name",)

    def has_module_permission(self, request):
        return is_admin_or_superuser(request.user)

    def has_view_permission(self, request, obj=None):
        return is_admin_or_superuser(request.user)

    def has_add_permission(self, request):
        return is_admin_or_superuser(request.user)

    def has_change_permission(self, request, obj=None):
        return is_admin_or_superuser(request.user)

    def has_delete_permission(self, request, obj=None):
        return is_admin_or_superuser(request.user)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "price", "stock", "is_hot", "is_active")
    list_filter = ("is_hot", "is_active", "category")
    search_fields = ("name", "subtitle")
    inlines = [ProductImageInline]

    def has_module_permission(self, request):
        return is_admin_or_superuser(request.user)

    def has_view_permission(self, request, obj=None):
        return is_admin_or_superuser(request.user)

    def has_add_permission(self, request):
        return is_admin_or_superuser(request.user)

    def has_change_permission(self, request, obj=None):
        return is_admin_or_superuser(request.user)

    def has_delete_permission(self, request, obj=None):
        return is_admin_or_superuser(request.user)


@admin.register(HomeBanner)
class HomeBannerAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "is_active", "sort")
    list_filter = ("is_active",)
    search_fields = ("title",)

    def has_module_permission(self, request):
        return is_admin_or_superuser(request.user)

    def has_view_permission(self, request, obj=None):
        return is_admin_or_superuser(request.user)

    def has_add_permission(self, request):
        return is_admin_or_superuser(request.user)

    def has_change_permission(self, request, obj=None):
        return is_admin_or_superuser(request.user)

    def has_delete_permission(self, request, obj=None):
        return is_admin_or_superuser(request.user)


@admin.register(ServiceMessage)
class ServiceMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "user", "created_at")
    search_fields = ("product__name", "user__username", "content")

    def has_module_permission(self, request):
        return is_admin_or_superuser(request.user) or is_merchant(request.user)

    def has_view_permission(self, request, obj=None):
        return is_admin_or_superuser(request.user) or is_merchant(request.user)

    def has_add_permission(self, request):
        return is_admin_or_superuser(request.user)

    def has_change_permission(self, request, obj=None):
        return is_admin_or_superuser(request.user) or is_merchant(request.user)

    def has_delete_permission(self, request, obj=None):
        return is_admin_or_superuser(request.user)

    def get_readonly_fields(self, request, obj=None):
        if is_merchant(request.user):
            return ("product", "user", "content", "created_at")
        return ()
