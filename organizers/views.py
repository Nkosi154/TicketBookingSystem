from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from events.models import Event
from tickets.models import Ticket
from discounts.models import DiscountCode
from django.shortcuts import render


def home(request):
    return render(request, 'base.html')

@login_required
def dashboard(request):
    events = Event.objects.filter(
        organizer=request.user
    ).order_by('-created_at')

    total_revenue = Ticket.objects.filter(
        event__organizer=request.user,
        status__in=['active', 'used']
    ).aggregate(total=Sum('price_paid'))['total'] or 0

    total_tickets_sold = Ticket.objects.filter(
        event__organizer=request.user,
        status__in=['active', 'used']
    ).count()

    return render(request, 'organizers/dashboard.html', {
        'events': events,
        'total_revenue': total_revenue,
        'total_tickets_sold': total_tickets_sold,
    })


@login_required
def event_stats(request, event_pk):
    event = get_object_or_404(Event, pk=event_pk, organizer=request.user)

    tickets = Ticket.objects.filter(event=event).order_by('-purchased_at')

    revenue = tickets.filter(
        status__in=['active', 'used']
    ).aggregate(total=Sum('price_paid'))['total'] or 0

    tickets_sold = tickets.filter(status__in=['active', 'used']).count()
    tickets_used = tickets.filter(status='used').count()
    tickets_active = tickets.filter(status='active').count()

    discount_codes = DiscountCode.objects.filter(event=event)

    return render(request, 'organizers/event_stats.html', {
        'event': event,
        'tickets': tickets,
        'revenue': revenue,
        'tickets_sold': tickets_sold,
        'tickets_used': tickets_used,
        'tickets_active': tickets_active,
        'discount_codes': discount_codes,
    })


@login_required
def create_event(request):
    from events.forms import EventForm

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.tickets_remaining = event.total_tickets
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('dashboard')
    else:
        form = EventForm()

    return render(request, 'organizers/create_event.html', {'form': form})


@login_required
def create_discount_code(request, event_pk):
    event = get_object_or_404(Event, pk=event_pk, organizer=request.user)

    if request.method == 'POST':
        from discounts.forms import DiscountCodeForm
        form = DiscountCodeForm(request.POST)
        if form.is_valid():
            discount = form.save(commit=False)
            discount.event = event
            discount.created_by = request.user
            discount.save()
            messages.success(request, f'Discount code {discount.code} created!')
            return redirect('event_stats', event_pk=event.pk)
    else:
        from discounts.forms import DiscountCodeForm
        form = DiscountCodeForm()

    return render(request, 'organizers/create_discount_code.html', {
        'form': form,
        'event': event
    })
@login_required
def create_event(request):
    if not request.user.is_staff and not request.user.has_active_subscription():
        messages.error(request, 'You need an active subscription to create events.')
        return redirect('subscription_pricing')
