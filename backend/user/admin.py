from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Address, User


@admin.register(User)
class MallUserAdmin(UserAdmin):
	fieldsets = UserAdmin.fieldsets + (("扩展信息", {"fields": ("avatar",)}),)
	add_fieldsets = UserAdmin.add_fieldsets + (("扩展信息", {"fields": ("email", "avatar")}),)
	list_display = ("id", "username", "email", "is_staff", "is_active", "date_joined")
	search_fields = ("username", "email")


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "name", "phone", "province", "city", "is_default")
	search_fields = ("user__username", "name", "phone", "detail")
	list_filter = ("is_default", "province", "city")
