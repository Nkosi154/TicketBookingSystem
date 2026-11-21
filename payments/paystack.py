import requests
from django.conf import settings


PAYSTACK_BASE_URL = 'https://api.paystack.co'


def initialize_payment(email, amount, reference, callback_url, metadata=None):
    """
    Start a payment on Paystack.
    Returns the authorization URL to redirect the user to.
    amount must be in kobo/cents (R300 = 30000)
    """
    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        'Content-Type': 'application/json',
    }

    data = {
        'email': email,
        'amount': amount,
        'reference': str(reference),
        'callback_url': callback_url,
        'currency': 'ZAR',
        'metadata': metadata or {},
    }

    response = requests.post(
        f'{PAYSTACK_BASE_URL}/transaction/initialize',
        json=data,
        headers=headers
    )

    result = response.json()

    if result.get('status'):
        return {
            'success': True,
            'authorization_url': result['data']['authorization_url'],
            'reference': result['data']['reference'],
        }

    return {'success': False, 'message': result.get('message', 'Payment init failed')}


def verify_payment(reference):
    """
    Verify a payment after Paystack redirects back.
    Returns True if payment was successful.
    """
    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
    }

    response = requests.get(
        f'{PAYSTACK_BASE_URL}/transaction/verify/{reference}',
        headers=headers
    )

    result = response.json()

    if result.get('status') and result['data']['status'] == 'success':
        return {
            'success': True,
            'amount': result['data']['amount'],
            'reference': result['data']['reference'],
            'email': result['data']['customer']['email'],
        }

    return {'success': False}
