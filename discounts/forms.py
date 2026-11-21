from django import forms
from .models import DiscountCode

class DiscountCodeForm(forms.ModelForm):
    class Meta:
        model = DiscountCode
        fields = [
            'code',
            'discount_type',
            'value',
            'students_only',
            'max_uses',
            'valid_from',
            'valid_until',
            'is_active',
        ]
        widgets = {
            'valid_from': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'valid_until': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }