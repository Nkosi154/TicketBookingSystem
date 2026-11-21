from django.urls import path
from . import views

urlpatterns = [
    path('buy/<int:event_pk>/', views.buy_ticket, name='buy_ticket'),
    path('my-tickets/', views.my_tickets, name='my_tickets'),
    path('<int:pk>/', views.ticket_detail, name='ticket_detail'),
    path('validate/', views.validate_ticket, name='validate_ticket'),
    path('mark-used/<uuid:ticket_uuid>/', views.mark_ticket_used, name='mark_ticket_used'),
]