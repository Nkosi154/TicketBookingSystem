import uuid
import qrcode
import os
from django.db import models
from django.conf import settings
from events.models import Event

class Ticket(models.Model):

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('used', 'Used'),
        ('cancelled', 'Cancelled'),
    ]

    ticket_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='tickets'
    )
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tickets'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    qr_code = models.ImageField(
        upload_to='qr_codes/',
        blank=True
    )
    purchased_at = models.DateTimeField(auto_now_add=True)
    price_paid = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"Ticket {self.ticket_id} - {self.event.title}"

    def generate_qr_code(self):
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(str(self.ticket_id))
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        qr_filename = f"qr_codes/ticket_{self.ticket_id}.png"
        qr_path = os.path.join(settings.MEDIA_ROOT, qr_filename)

        os.makedirs(os.path.dirname(qr_path), exist_ok=True)
        img.save(qr_path)

        self.qr_code = qr_filename
        self.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.qr_code:
            self.generate_qr_code()