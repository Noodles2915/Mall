from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Address, User


@admin.register(User)
class MallUserAdmin(UserAdmin):
	fieldsets = UserAdmin.fieldsets + (("扩展信息", {"fields": ("avatar", "role")}),)
	add_fieldsets = UserAdmin.add_fieldsets + (("扩展信息", {"fields": ("email", "avatar", "role")}),)
	list_display = ("id", "username", "email", "role", "is_staff", "is_active", "date_joined")
	search_fields = ("username", "email")
	list_filter = ("role", "is_staff", "is_active")

	def has_module_permission(self, request):
		return request.user.is_superuser or request.user.is_admin_role

	def has_view_permission(self, request, obj=None):
		return request.user.is_superuser or request.user.is_admin_role

	def has_add_permission(self, request):
		return request.user.is_superuser or request.user.is_admin_role

	def has_change_permission(self, request, obj=None):
		return request.user.is_superuser or request.user.is_admin_role

	def has_delete_permission(self, request, obj=None):
		return request.user.is_superuser or request.user.is_admin_role


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "name", "phone", "province", "city", "is_default")
	search_fields = ("user__username", "name", "phone", "detail")
	list_filter = ("is_default", "province", "city")

	def has_module_permission(self, request):
		return request.user.is_superuser or request.user.is_admin_role

	def has_view_permission(self, request, obj=None):
		return request.user.is_superuser or request.user.is_admin_role

	def has_add_permission(self, request):
		return request.user.is_superuser or request.user.is_admin_role

	def has_change_permission(self, request, obj=None):
		return request.user.is_superuser or request.user.is_admin_role

	def has_delete_permission(self, request, obj=None):
		return request.user.is_superuser or request.user.is_admin_role
