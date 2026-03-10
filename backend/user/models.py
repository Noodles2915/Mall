from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

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
