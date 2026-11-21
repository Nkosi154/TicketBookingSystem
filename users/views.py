from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import RegisterForm
from .student_domains import is_valid_student_domain

User = get_user_model()


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('event_list')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('event_list')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def verify_student(request):
    if request.method == 'POST':
        student_email = request.POST.get('student_email', '').strip().lower()

        if not is_valid_student_domain(student_email):
            messages.error(request, 'That email is not from a recognised South African university.')
            return render(request, 'users/verify_student.html')

        code = request.user.generate_verification_code()
        request.user.student_email = student_email
        request.user.save()

        send_mail(
            subject='TicketFlow — Student Verification Code',
            message=f'Your student verification code is: {code}\n\nThis code expires in 10 minutes.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[student_email],
        )

        messages.success(request, f'Code sent to {student_email}. Check your inbox.')
        return redirect('verify_student_code')

    return render(request, 'users/verify_student.html')


@login_required
def verify_student_code(request):
    if request.method == 'POST':
        entered_code = request.POST.get('code', '').strip()

        if entered_code == request.user.verification_code:
            request.user.is_student = True
            request.user.student_verified = True
            request.user.verification_code = ''
            request.user.save()
            messages.success(request, 'Student status verified! You can now access student discounts.')
            return redirect('event_list')
        else:
            messages.error(request, 'Incorrect code. Please try again.')

    return render(request, 'users/verify_student_code.html')