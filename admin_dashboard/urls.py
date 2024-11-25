from django.urls import path
from .views import admin_dashboard, employee_list,  leave_requests_view, reports_view, add_employee, edit_employee, admin_login, admin_redirect, employee_detail, approve_leave_request, reject_leave_request, create_leave, detailed_work_report, mark_notification_as_read

urlpatterns = [
    path('', admin_redirect, name='admin-redirect'),  # Main admin URL
    path('dashboard/', admin_dashboard, name='admin-dashboard'),
    path('login/', admin_login, name='admin-login'),
    path('employees/', employee_list, name='admin-employee-list'),  
    path('employees/add/', add_employee, name='add-employee'),
    path('employees/edit/<int:pk>/', edit_employee, name='edit-employee'),
    path('employees/<int:pk>/', employee_detail, name='employee-detail'),
    path('leave-requests/', leave_requests_view, name='admin-leave-requests'),
    path('leave-requests/approve/<int:pk>/', approve_leave_request, name='approve-leave-request'),
    path('leave-requests/reject/<int:pk>/', reject_leave_request, name='reject-leave-request'),  
    path('reports/', reports_view, name='admin-reports'),
    path('leave-requests/create/', create_leave, name='create-leave'),
    path('detailed-work-report/', detailed_work_report, name='detailed-work-report'),
    path('notifications/<int:pk>/read/', mark_notification_as_read, name='mark-notification-as-read'),
]
