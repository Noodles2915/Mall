from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q

from utils import avatar_path


class User(AbstractUser):
    ROLE_NORMAL = "normal"
    ROLE_ADMIN = "admin"
    ROLE_MERCHANT = "merchant"
    ROLE_CHOICES = [
        (ROLE_NORMAL, "普通用户"),
        (ROLE_ADMIN, "管理员"),
        (ROLE_MERCHANT, "商家"),
    ]

    email = models.EmailField(verbose_name="邮箱", unique=True)
    avatar = models.ImageField(verbose_name="头像", null=True, blank=True, upload_to=avatar_path)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_NORMAL, verbose_name="角色")

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = self.ROLE_ADMIN

        self.is_staff = self.role in {self.ROLE_ADMIN, self.ROLE_MERCHANT}
        super().save(*args, **kwargs)

    @property
    def is_admin_role(self):
        return self.role == self.ROLE_ADMIN

    @property
    def is_merchant_role(self):
        return self.role == self.ROLE_MERCHANT

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = "用户"

    def __str__(self):
        return self.username


class Address(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="addresses",
        verbose_name="用户"
    )
    name = models.CharField(max_length=50, verbose_name="收货人姓名")
    phone = models.CharField(max_length=20, verbose_name="联系电话")
    province = models.CharField(max_length=20, verbose_name="省份")
    city = models.CharField(max_length=20, verbose_name="城市")
    district = models.CharField(max_length=20, verbose_name="区县")
    detail = models.CharField(max_length=100, verbose_name="详细地址")
    is_default = models.BooleanField(default=False, verbose_name="是否默认地址")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "收货地址"
        verbose_name_plural = "收货地址"
        ordering = ["-is_default", "-id"]

    def __str__(self):
        return f"{self.name} {self.phone} {self.detail}"


class QualificationApplication(models.Model):
    TYPE_MERCHANT = "merchant"
    TYPE_STAFF = "staff"
    TYPE_CHOICES = [
        (TYPE_MERCHANT, "商家资质"),
        (TYPE_STAFF, "工作人员资质"),
    ]

    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_CHOICES = [
        (STATUS_PENDING, "待审核"),
        (STATUS_APPROVED, "已通过"),
        (STATUS_REJECTED, "已驳回"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="qualification_applications",
        verbose_name="申请用户",
    )
    application_type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="申请类型")
    reason = models.TextField(max_length=1000, verbose_name="申请说明")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name="审核状态",
    )
    review_note = models.CharField(max_length=255, blank=True, default="", verbose_name="审核备注")
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_qualification_applications",
        verbose_name="审核人",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name="审核时间")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "资质申请"
        verbose_name_plural = "资质申请"
        ordering = ["-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "application_type", "status"],
                condition=Q(status="pending"),
                name="uniq_pending_qualification_application",
            )
        ]

    def __str__(self):
        return f"{self.user.username}-{self.get_application_type_display()}-{self.get_status_display()}"
