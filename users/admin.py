from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Extra Info',{'fields':('is_student','university','phone_number')}),
    )
    list_display = ['email','username','is_student','university']
