from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('event/create/', views.create_event, name='create_event'),
    path('event/<int:event_pk>/stats/', views.event_stats, name='event_stats'),
    path('event/<int:event_pk>/discount/create/', views.create_discount_code, name='create_discount_code'),
]