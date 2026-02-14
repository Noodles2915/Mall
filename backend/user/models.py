from django.db import models

import hashlib

from utils import avatar_path

class User(models.Model):

    username = models.CharField(verbose_name="用户名", max_length=50)
    email = models.EmailField(verbose_name="邮箱", unique=True)
    password = models.CharField(verbose_name="密码", max_length=255)
    salt = models.CharField(verbose_name="盐", max_length=15)
    avatar = models.ImageField(verbose_name="头像", null=True, blank=True, upload_to=avatar_path)

    def __str__(self):
        return self.username
    
    def encrypt_password(self, password: str):
        salt = hashlib.sha1(self.username.encode()).hexdigest()
        self.salt = salt
        self.pw = hashlib.sha256((password + salt).encode()).hexdigest()

    def check_password(self, password: str) -> bool:
        hash_pw = hashlib.sha256((password + self.salt).encode()).hexdigest()
        return hash_pw == self.pw
