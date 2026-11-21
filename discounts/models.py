from django.db import models
from django.conf import settings
from django.utils import timezone
from events.models import Event


class DiscountCode(models.Model):

    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]

    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(
        max_length=20,
        choices=DISCOUNT_TYPE_CHOICES,
        default='percentage'
    )
    value = models.DecimalField(max_digits=6, decimal_places=2)
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='discount_codes',
        null=True,
        blank=True
    )
    students_only = models.BooleanField(default=True)
    max_uses = models.PositiveIntegerField(default=1)
    times_used = models.PositiveIntegerField(default=0)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='discount_codes'
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} — {self.value}{'%' if self.discount_type == 'percentage' else 'R'} off"

    def is_valid(self, user):
      now = timezone.now()

      if not self.is_active:
        return False, 'This discount code is inactive.'
      if now < self.valid_from:
        return False, 'This discount code is not active yet.'
      if now > self.valid_until:
        return False, 'This discount code has expired.'
      if self.times_used >= self.max_uses:
        return False, 'This discount code has reached its usage limit.'
      if self.students_only and not user.is_student:
        return False, 'This discount is for students only.'
      if self.students_only and not user.student_verified:
        return False, 'You need to verify your student email first.'

      return True, 'Valid'

    def calculate_discount(self, original_price):
        if self.discount_type == 'percentage':
            discount = (self.value / 100) * original_price
        else:
            discount = self.value

        final_price = original_price - discount
        return max(final_price, 0)