from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
import random

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username and not email:
            raise ValueError("Either username or email must be provided")
        email = self.normalize_email(email) if email else None
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)
        return self.create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    full_name = models.CharField(max_length=100, null=True, blank=True)

    profile_picture = models.URLField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)

    address = models.JSONField(default=dict, null=True, blank=True)
    external_links = models.JSONField(default=dict, null=True, blank=True)
    about = models.CharField(max_length=250, null=True, blank=True)

    is_admin = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.username

    @property
    def is_staff(self):
        return self.is_admin
    
class EmailOTP(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='otp_codes')
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'email_otps'
        ordering = ['-created_at']
    
    def is_expired(self):
        expiry_time = self.created_at + timezone.timedelta(minutes=3)
        return timezone.now() > expiry_time
    
    @staticmethod
    def generate_otp():
        """6 digit random OTP"""
        return str(random.randint(100000, 999999))
    
    def __str__(self):
        return f"{self.user.username} - {self.otp}"