from django.urls import path
from . import views

urlpatterns = [
    path('ticket/<int:event_pk>/', views.initiate_ticket_payment, name='initiate_ticket_payment'),
    path('verify/ticket/<uuid:reference>/', views.verify_ticket_payment, name='verify_ticket_payment'),
    path('subscribe/', views.initiate_subscription_payment, name='initiate_subscription_payment'),
    path('verify/subscription/<uuid:reference>/', views.verify_subscription_payment, name='verify_subscription_payment'),
]