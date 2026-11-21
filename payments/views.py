from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from events.models import Event
from tickets.models import Ticket
from discounts.models import DiscountCode
from .models import Payment
from .paystack import initialize_payment, verify_payment
import uuid


@login_required
def initiate_ticket_payment(request, event_pk):
    event = get_object_or_404(Event, pk=event_pk)

    if event.is_sold_out():
        messages.error(request, 'Sorry this event is sold out.')
        return redirect('event_detail', pk=event_pk)

    # calculate price with optional discount
    final_price = event.price
    discount = None
    discount_code_id = request.GET.get('discount_code_id')

    if discount_code_id:
        try:
            discount = DiscountCode.objects.get(pk=discount_code_id)
            valid, message = discount.is_valid(request.user)
            if valid:
                final_price = discount.calculate_discount(event.price)
        except DiscountCode.DoesNotExist:
            pass

    # amount in kobo/cents
    amount_kobo = int(final_price * 100)

    # commission TicketFlow takes
    commission_kobo = int(amount_kobo * settings.COMMISSION_PERCENT / 100)

    # create pending payment record
    payment = Payment.objects.create(
        user=request.user,
        payment_type='ticket',
        amount=amount_kobo,
        commission=commission_kobo,
        status='pending',
        event=event,
    )

    # build callback URL
    callback_url = request.build_absolute_uri(
        reverse('verify_ticket_payment', args=[payment.reference])
    )
    if discount_code_id:
        callback_url += f'?discount_code_id={discount_code_id}'

    # initialize with Paystack
    result = initialize_payment(
        email=request.user.email,
        amount=amount_kobo,
        reference=payment.reference,
        callback_url=callback_url,
        metadata={
            'event_id': event.pk,
            'event_title': event.title,
            'user_id': request.user.pk,
        }
    )

    if result['success']:
        payment.paystack_reference = result['reference']
        payment.save()
        return redirect(result['authorization_url'])

    messages.error(request, 'Payment initialization failed. Try again.')
    return redirect('event_detail', pk=event_pk)


@login_required
def verify_ticket_payment(request, reference):
    payment = get_object_or_404(Payment, reference=reference, user=request.user)

    # already verified — just show the ticket
    if payment.status == 'success':
        if payment.ticket:
            return redirect('ticket_detail', pk=payment.ticket.pk)
        return redirect('my_tickets')

    # verify with Paystack
    paystack_result = verify_payment(payment.paystack_reference)

    if paystack_result['success']:
        # create the ticket
        ticket = Ticket.objects.create(
            event=payment.event,
            buyer=request.user,
            price_paid=payment.amount_in_rands(),
        )

        # update payment record
        payment.status = 'success'
        payment.ticket = ticket
        payment.verified_at = timezone.now()
        payment.save()

        # reduce ticket count
        payment.event.tickets_remaining -= 1
        payment.event.save()

        # increment discount usage if applicable
        discount_code_id = request.GET.get('discount_code_id')
        if discount_code_id:
            try:
                discount = DiscountCode.objects.get(pk=discount_code_id)
                discount.times_used += 1
                discount.save()
            except DiscountCode.DoesNotExist:
                pass

        messages.success(request, 'Payment successful! Your ticket is ready. 🎟')
        return redirect('ticket_detail', pk=ticket.pk)

    else:
        payment.status = 'failed'
        payment.save()
        messages.error(request, 'Payment could not be verified. Contact support if money was deducted.')
        return redirect('event_list')


@login_required
def initiate_subscription_payment(request):
    amount_kobo = settings.SUBSCRIPTION_PRICE  # 14900 = R149.00

    payment = Payment.objects.create(
        user=request.user,
        payment_type='subscription',
        amount=amount_kobo,
        commission=0,
        status='pending',
    )

    callback_url = request.build_absolute_uri(
        reverse('verify_subscription_payment', args=[payment.reference])
    )

    result = initialize_payment(
        email=request.user.email,
        amount=amount_kobo,
        reference=payment.reference,
        callback_url=callback_url,
        metadata={
            'user_id': request.user.pk,
            'payment_type': 'subscription',
        }
    )

    if result['success']:
        payment.paystack_reference = result['reference']
        payment.save()
        return redirect(result['authorization_url'])

    messages.error(request, 'Subscription payment failed to initialize.')
    return redirect('dashboard')


@login_required
def verify_subscription_payment(request, reference):
    payment = get_object_or_404(Payment, reference=reference, user=request.user)

    if payment.status == 'success':
        return redirect('dashboard')

    paystack_result = verify_payment(payment.paystack_reference)

    if paystack_result['success']:
        payment.status = 'success'
        payment.verified_at = timezone.now()
        payment.save()

        # mark user as active organizer
        request.user.is_subscribed = True
        request.user.subscription_expires = timezone.now() + timezone.timedelta(days=30)
        request.user.save()

        messages.success(request, 'Subscription activated! You can now create events.')
        return redirect('create_event')

    else:
        payment.status = 'failed'
        payment.save()
        messages.error(request, 'Subscription payment failed.')
        return redirect('dashboard')