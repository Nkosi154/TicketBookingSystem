from django.contrib.auth.models import AbstractUser
from django.db import models
import random

class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    university = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    student_email = models.EmailField(blank=True)
    student_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, blank=True)

    def __str__(self):
        return self.email

    def generate_verification_code(self):
        # generates a random 6 digit code
        self.verification_code = str(random.randint(100000, 999999))
        self.save()
        return self.verification_code

is_subscribed = models.BooleanField(default=False)
subscription_expires = models.DateTimeField(null=True, blank=True)

def has_active_subscription(self):
    from django.utils import timezone
    if not self.is_subscribed:
        return False
    if self.subscription_expires and timezone.now() > self.subscription_expires:
        self.is_subscribed = False
        self.save()
        return False
    return True