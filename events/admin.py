from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'organizer', 'date', 'city', 'price', 'tickets_remaining', 'status']
    list_filter = ['status', 'city']
    search_fields = ['title', 'venue', 'city']