from django.contrib import admin
from django.contrib import messages
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone

from .models import Address, QualificationApplication, User


def _can_access_admin(user):
	return bool(
		getattr(user, "is_authenticated", False)
		and (getattr(user, "is_superuser", False) or getattr(user, "is_admin_role", False))
	)


@admin.register(User)
class MallUserAdmin(UserAdmin):
	fieldsets = UserAdmin.fieldsets + (("扩展信息", {"fields": ("avatar", "role")}),)
	add_fieldsets = UserAdmin.add_fieldsets + (("扩展信息", {"fields": ("email", "avatar", "role")}),)
	list_display = ("id", "username", "email", "role", "is_staff", "is_active", "date_joined")
	search_fields = ("username", "email")
	list_filter = ("role", "is_staff", "is_active")

	def has_module_permission(self, request):
		return _can_access_admin(request.user)

	def has_view_permission(self, request, obj=None):
		return _can_access_admin(request.user)

	def has_add_permission(self, request):
		return _can_access_admin(request.user)

	def has_change_permission(self, request, obj=None):
		return _can_access_admin(request.user)

	def has_delete_permission(self, request, obj=None):
		return _can_access_admin(request.user)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "name", "phone", "province", "city", "is_default")
	search_fields = ("user__username", "name", "phone", "detail")
	list_filter = ("is_default", "province", "city")

	def has_module_permission(self, request):
		return _can_access_admin(request.user)

	def has_view_permission(self, request, obj=None):
		return _can_access_admin(request.user)

	def has_add_permission(self, request):
		return _can_access_admin(request.user)

	def has_change_permission(self, request, obj=None):
		return _can_access_admin(request.user)

	def has_delete_permission(self, request, obj=None):
		return _can_access_admin(request.user)


@admin.register(QualificationApplication)
class QualificationApplicationAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "application_type", "status", "reviewed_by", "reviewed_at", "created_at")
	search_fields = ("user__username", "reason", "review_note")
	list_filter = ("application_type", "status", "created_at")
	readonly_fields = ("user", "application_type", "reason", "created_at", "updated_at", "reviewed_by", "reviewed_at")
	actions = ("approve_selected", "reject_selected")

	@admin.action(description="审核通过（选中项）")
	def approve_selected(self, request, queryset):
		pending_items = queryset.filter(status=QualificationApplication.STATUS_PENDING)
		count = 0
		for application in pending_items:
			self._apply_review(application, request.user, QualificationApplication.STATUS_APPROVED, "后台批量审核通过")
			count += 1
		self.message_user(request, f"已通过 {count} 条资质申请")

	@admin.action(description="审核驳回（选中项）")
	def reject_selected(self, request, queryset):
		pending_items = queryset.filter(status=QualificationApplication.STATUS_PENDING)
		count = 0
		for application in pending_items:
			self._apply_review(application, request.user, QualificationApplication.STATUS_REJECTED, "后台批量审核驳回")
			count += 1
		self.message_user(request, f"已驳回 {count} 条资质申请")

	def _apply_review(self, application, reviewer, status_value, review_note):
		application.status = status_value
		application.review_note = review_note.strip()
		application.reviewed_by = reviewer
		application.reviewed_at = timezone.now()
		application.save(update_fields=["status", "review_note", "reviewed_by", "reviewed_at", "updated_at"])

		if (
			application.application_type == QualificationApplication.TYPE_MERCHANT
			and status_value == QualificationApplication.STATUS_APPROVED
			and application.user.role != User.ROLE_ADMIN
		):
			application.user.role = User.ROLE_MERCHANT
			application.user.save(update_fields=["role", "is_staff"])

	def save_model(self, request, obj, form, change):
		if change:
			old_obj = QualificationApplication.objects.get(pk=obj.pk)
			status_changed = old_obj.status != obj.status
			if status_changed and old_obj.status != QualificationApplication.STATUS_PENDING:
				obj.status = old_obj.status
				self.message_user(request, "已审核申请不支持重复审核", level=messages.WARNING)
				return

			if status_changed:
				note = (obj.review_note or "").strip()
				if obj.status == QualificationApplication.STATUS_REJECTED and not note:
					obj.review_note = "后台审核驳回"
				obj.reviewed_by = request.user
				obj.reviewed_at = timezone.now()

		super().save_model(request, obj, form, change)

		if change and obj.status == QualificationApplication.STATUS_APPROVED:
			if obj.application_type == QualificationApplication.TYPE_MERCHANT and obj.user.role != User.ROLE_ADMIN:
				obj.user.role = User.ROLE_MERCHANT
				obj.user.save(update_fields=["role", "is_staff"])

	def has_module_permission(self, request):
		return _can_access_admin(request.user)

	def has_view_permission(self, request, obj=None):
		return _can_access_admin(request.user)

	def has_add_permission(self, request):
		return _can_access_admin(request.user)

	def has_change_permission(self, request, obj=None):
		return _can_access_admin(request.user)

	def has_delete_permission(self, request, obj=None):
		return _can_access_admin(request.user)
