# Add these to your ticketflow/views.py (create this file if it doesn't exist)
from django.shortcuts import render, redirect
from django.contrib import messages


def about(request):
    return render(request, 'about.html')


def contact(request):
    sent = False
    if request.method == 'POST':
        # For now just show success — we'll wire email later
        name = request.POST.get('name')
        messages.success(request, f"Thanks {name}! We'll be in touch soon.")
        sent = True
    return render(request, 'contact.html', {'sent': sent})

def subscription_pricing(request):
    return render(request, 'pricing.html', {
        'price': 149,
        'commission': 5,
    })