from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from events.models import Event
from .models import Ticket
from discounts.models import DiscountCode
import uuid


@login_required
def buy_ticket(request, event_pk):
    event = get_object_or_404(Event, pk=event_pk)
    discount = None
    final_price = event.price
    discount_message = None

    if event.is_sold_out():
        messages.error(request, 'Sorry, this event is sold out.')
        return redirect('event_detail', pk=event_pk)

    if request.method == 'POST':
        action = request.POST.get('action')

        # ── Apply discount code ──────────────────────────────────
        if action == 'apply_code':
            code_input = request.POST.get('discount_code', '').strip().upper()
            try:
                discount = DiscountCode.objects.get(code=code_input)
                valid, message = discount.is_valid(request.user)
                if valid:
                    final_price = discount.calculate_discount(event.price)
                    discount_message = f'Code applied! You save R{event.price - final_price:.2f}'
                else:
                    discount = None
                    discount_message = message
                    messages.error(request, message)
            except DiscountCode.DoesNotExist:
                discount_message = 'Invalid discount code.'
                messages.error(request, 'Invalid discount code.')

            return render(request, 'tickets/buy_ticket.html', {
                'event': event,
                'discount': discount,
                'final_price': final_price,
                'discount_message': discount_message,
            })

        # ── Confirm purchase → redirect to Paystack ──────────────
        elif action == 'confirm_purchase':
            discount_code_id = request.POST.get('discount_code_id', '')
            url = reverse('initiate_ticket_payment', args=[event.pk])
            if discount_code_id:
                url += f'?discount_code_id={discount_code_id}'
            return redirect(url)

    return render(request, 'tickets/buy_ticket.html', {
        'event': event,
        'final_price': final_price,
        'discount': discount,
        'discount_message': discount_message,
    })


@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk, buyer=request.user)
    return render(request, 'tickets/ticket_detail.html', {'ticket': ticket})


@login_required
def my_tickets(request):
    tickets = Ticket.objects.filter(
        buyer=request.user
    ).order_by('-purchased_at')
    return render(request, 'tickets/my_tickets.html', {'tickets': tickets})


@login_required
def validate_ticket(request):
    # only staff or organizers can access the scanner
    if not request.user.is_staff and not request.user.events.exists():
        raise PermissionDenied

    ticket = None
    error = None

    if request.method == 'POST':
        if 'ticket_id' in request.POST:
            ticket_id = request.POST.get('ticket_id', '').strip()
            ticket, error = lookup_ticket(ticket_id)

        elif 'qr_image' in request.FILES:
            try:
                from PIL import Image
                import numpy as np
                import cv2
                from pyzbar.pyzbar import decode

                image_file = request.FILES['qr_image']
                image = Image.open(image_file)
                image_np = np.array(image)
                gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
                decoded_objects = decode(gray)

                if decoded_objects:
                    qr_data = decoded_objects[0].data.decode('utf-8')
                    ticket, error = lookup_ticket(qr_data)
                else:
                    error = 'No QR code found in the image. Try again with a clearer photo.'

            except Exception:
                error = 'Could not process image. Please try again.'

    return render(request, 'tickets/validate_ticket.html', {
        'ticket': ticket,
        'error': error,
    })


def lookup_ticket(ticket_id_str):
    """
    Takes a ticket ID string, returns (ticket, error).
    One of them will always be None.
    """
    try:
        ticket_uuid = uuid.UUID(ticket_id_str)
        ticket = Ticket.objects.get(ticket_id=ticket_uuid)

        if ticket.status == 'used':
            return None, 'This ticket has already been used.'
        elif ticket.status == 'cancelled':
            return None, 'This ticket has been cancelled.'

        return ticket, None

    except (ValueError, Ticket.DoesNotExist):
        return None, 'Invalid ticket. No matching ticket found.'


@login_required
def mark_ticket_used(request, ticket_uuid):
    # only staff or organizers can mark tickets as used
    if not request.user.is_staff and not request.user.events.exists():
        raise PermissionDenied

    ticket = get_object_or_404(Ticket, ticket_id=ticket_uuid)

    if request.method == 'POST':
        if ticket.status == 'active':
            ticket.status = 'used'
            ticket.save()
            messages.success(
                request,
                f'Ticket for {ticket.event.title} marked as used. ✅'
            )
        else:
            messages.error(
                request,
                f'Ticket is already {ticket.status}.'
            )

    return redirect('validate_ticket')