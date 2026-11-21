from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('verify-student/', views.verify_student, name='verify_student'),
    path('verify-student/code/', views.verify_student_code, name='verify_student_code'),
]