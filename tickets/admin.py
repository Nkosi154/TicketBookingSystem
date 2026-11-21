from django.contrib import admin
from .models import Ticket

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_id', 'event', 'buyer', 'status', 'price_paid', 'purchased_at']
    list_filter = ['status', 'event']
    readonly_fields = ['ticket_id', 'qr_code', 'purchased_at']