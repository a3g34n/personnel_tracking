from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from leave_management.models import Leave
from django.utils.timezone import now
from rest_framework.test import APIRequestFactory
from attendance.views import CheckinView
from django.contrib import messages
from django.shortcuts import get_object_or_404
from datetime import datetime

@login_required(login_url='/employee/login/')
def employee_redirect(request):
    if request.user.role == 'employee':  # Check if the user is an employee
        return redirect('employee-dashboard')  # Redirect to the employee dashboard
    return redirect('employee-login')  # Redirect to the employee login page
def employee_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.role == 'employee':  # Employee user check
            login(request, user)

              # Trigger CheckinView programmatically
            factory = APIRequestFactory()
            checkin_request = factory.post('/api/attendance/checkin/', {}, format='json')
            checkin_request.user = user  # Attach the logged-in user
            response = CheckinView.as_view()(checkin_request)

            if response.status_code != 200:  # Handle any errors returned by CheckinView
                return render(request, 'employee_dashboard/employee_login.html', {
                    'error': response.data.get('message', 'Failed to check in.'),
                })

            return redirect(request.GET.get('next', 'employee-dashboard'))  # Redirect to next or dashboard
        else:
            return render(request, 'employee_dashboard/employee_login.html', {'error': 'Invalid credentials or not an employee user.'})
    return render(request, 'employee_dashboard/employee_login.html')
def employee_dashboard(request):
    return render(request, 'employee_dashboard/dashboard.html')
def attendance_view(request):
    # Çalışanın giriş/çıkış kayıtlarını alalım (örnek veri)
    user_attendance = request.user.attendance_set.all()  # User ile Attendance arasında ForeignKey olduğunu varsayıyoruz
    return render(request, 'employee_dashboard/attendance.html', {'attendance': user_attendance})
def profile_view(request):
    # Çalışanın profil bilgilerini gösterelim
    return render(request, 'employee_dashboard/profile.html', {'user': request.user})
def leave_summary(request):
    user = request.user
    remaining_days = Leave.remaining_leave_days(user)  # Kalan izin günlerini hesapla

    approved_leaves = Leave.objects.filter(user=user, status='approved')  # Onaylanan izinler
    pending_leaves = Leave.objects.filter(user=user, status='pending')  # Bekleyen izinler

    context = {
        "remaining_days": remaining_days,
        "approved_leaves": approved_leaves,
        "pending_leaves": pending_leaves,
    }
    return render(request, 'employee_dashboard/leave_summary.html', context)
def leave_request_form(request):
    remaining_days = Leave.remaining_leave_days(request.user)  # Kullanıcının kalan izin günleri
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        reason = request.POST.get('reason')
        
        today = now().date()

        # İzin talebi oluştur
        if start_date and end_date:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()

            if start_date_obj < today or end_date_obj < today:
                messages.error(request, "You cannot request leave for past dates.")
                return render(request, 'employee_dashboard/leave_request_form.html')

            if start_date_obj > end_date_obj:
                messages.error(request, "Start date cannot be after end date.")
                return render(request, 'employee_dashboard/leave_request_form.html')

              # Talep edilen izin günlerini hesapla
            requested_days = (end_date_obj - start_date_obj).days + 1

            # Kullanıcının kalan izin günlerini kontrol et
            remaining_days = Leave.remaining_leave_days(request.user)
            if requested_days > remaining_days:
                messages.error(request, f"You cannot request {requested_days} days of leave. You only have {remaining_days:.2f} days remaining.")
                return render(request, 'employee_dashboard/leave_request_form.html', {'remaining_days': remaining_days})

            Leave.objects.create(
                user=request.user,
                start_date=start_date,
                end_date=end_date,
                reason=reason,
                status='pending'  # Varsayılan olarak "pending"
            )
            messages.success(request, "Your leave request has been submitted!")
            return redirect('leave-summary')  # Özet ekranına yönlendirin
        else:
            messages.error(request, "Start date and end date are required.")

    return render(request, 'employee_dashboard/leave_request_form.html', {'remaining_days': remaining_days})
def delete_leave_request(request, pk):
    leave = get_object_or_404(Leave, pk=pk, user=request.user, status='pending')  # Sadece pending izinler
    leave.delete()
    messages.success(request, "Your leave request has been deleted.")
    return redirect('leave-summary')