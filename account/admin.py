from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'full_name', 'is_active', 'is_verified', 'is_admin')
    list_filter = ('is_active', 'is_verified', 'is_admin', 'is_deleted')
    search_fields = ('username', 'email', 'full_name')
    ordering = ('username',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email', 'full_name', 'phone_number', 'date_of_birth', 'profile_picture', 'about')}),
        ('Address & Links', {'fields': ('address', 'external_links')}),
        ('Permissions', {'fields': ('is_active', 'is_verified', 'is_admin', 'is_superuser', 'groups', 'user_permissions')}),
        ('Status', {'fields': ('is_deleted',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_active', 'is_verified'),
        }),
    )
