from django.contrib import admin
from .models import DiscountCode

@admin.register(DiscountCode)
class DiscountCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'value', 'students_only',
                    'times_used', 'max_uses', 'valid_until', 'is_active']
    list_filter = ['students_only', 'is_active', 'discount_type']
    search_fields = ['code']