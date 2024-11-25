from django.urls import path
from .views import employee_dashboard, attendance_view, profile_view, employee_login, employee_redirect, leave_summary, leave_request_form, delete_leave_request

urlpatterns = [
    path('', employee_redirect, name='employee-redirect'),  # Main employee URL
    path('dashboard/', employee_dashboard, name='employee-dashboard'),
    path('login/', employee_login, name='employee-login'),
    path('attendance/', attendance_view, name='employee-attendance'),
    path('profile/', profile_view, name='employee-profile'),
    path('leave-summary/', leave_summary, name='leave-summary'),
    path('leave-request/', leave_request_form, name='leave-request'),
    path('leave-request/delete/<int:pk>/', delete_leave_request, name='delete-leave-request'),
]
