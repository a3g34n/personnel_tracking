from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login
from leave_management.models import Leave
from reports.models import Report  # Eğer bir Report modeli varsa kullanın
from django.contrib.auth import get_user_model
from .forms import EmployeeForm
from attendance.models import Attendance
from django.utils.timezone import now
from django.contrib import messages
from datetime import datetime, timedelta
from django.db.models import Sum, F, ExpressionWrapper, DurationField
from notifications.models import Notification


User = get_user_model()  # User modeline erişim sağlar

@login_required(login_url='/admin/login/')
def admin_redirect(request):
    if request.user.role == 'admin':  # Check if the user is an admin
        return redirect('admin-dashboard')  # Redirect to the admin dashboard
    return redirect('admin-login')  # Redirect to the admin login page
def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.role == 'admin':  # Admin user check
            login(request, user)
            return redirect(request.GET.get('next', 'admin-dashboard'))  # Redirect to next or dashboard
        else:
            return render(request, 'admin_dashboard/admin_login.html', {'error': 'Invalid credentials or not an admin user.'})
    return render(request, 'admin_dashboard/admin_login.html')
def admin_dashboard(request):
    today = now().date()
    late_attendances = Attendance.objects.filter(date=today).select_related('user')  # Bugünlük girişler

    # Sadece geç kalan çalışanları filtrele ve süresini hesapla
    late_employees = []
    for attendance in late_attendances:
        late_seconds = attendance.late_duration.total_seconds()
        late_hours = int(late_seconds // 3600)  # Saat
        late_minutes = int((late_seconds % 3600) // 60)  # Dakika
        late_employees.append({
            "username": attendance.user.username,
            "checkin_time": attendance.checkin_time,
            "late_duration_hours": late_hours,
            "late_duration_minutes": late_minutes,
        })

    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:10]

    return render(request, 'admin_dashboard/dashboard.html', {
        'late_employees': late_employees, 'notifications': notifications
    })
def add_employee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin-employee-list')  # Çalışan listesine yönlendir
    else:
        form = EmployeeForm()
    return render(request, 'admin_dashboard/add_employee.html', {'form': form})
def edit_employee(request, pk):
    employee = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('admin-employee-list')  # Çalışan listesine yönlendir
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'admin_dashboard/edit_employee.html', {'form': form, 'employee': employee})
def employee_list(request):
    today = now().date()
    
    # Get all employees and their attendance data for today
    employees = User.objects.filter(role='employee').select_related()  # Only employees
    employee_data = []

    for employee in employees:
        attendance = Attendance.objects.filter(user=employee, date=today).first()
        employee_data.append({
            "id": employee.id,  # Include the primary key
            "username": employee.username,
            "email": employee.email,
            "checkin_time": attendance.checkin_time if attendance else None,
            "checkout_time": attendance.checkout_time if attendance else None,
        })

    return render(request, 'admin_dashboard/employee_list.html', {'employee_data': employee_data})
def employee_detail(request, pk):
    # Çalışanı getir
    employee = get_object_or_404(User, pk=pk, role='employee')

    # Çalışanın bugünkü giriş-çıkış bilgilerini al
    today_attendance = Attendance.objects.filter(user=employee, date=now().date()).first()

    # Çalışanın geçmiş giriş-çıkış kayıtlarını al
    past_attendances = Attendance.objects.filter(user=employee).order_by('-date')

    # Çalışanın izin taleplerini alıyoruz
    leave_requests = Leave.objects.filter(user=employee).order_by('-start_date')

    # Çalışanın kalan izin günlerini hesaplıyoruz
    remaining_days = employee.remaining_leave_days()

    context = {
        "employee": employee,
        "today_attendance": today_attendance,
        "past_attendances": past_attendances,
        "leave_requests": leave_requests,
        "remaining_days": remaining_days
    }
    return render(request, 'admin_dashboard/employee_detail.html', context)
def leave_requests_view(request):
    leave_requests = Leave.objects.filter(status='pending').order_by('-created_at')
    return render(request, 'admin_dashboard/leave_requests.html', {'leave_requests': leave_requests})
def reports_view(request):
    # Örnek: Rapor verilerini ekleyin (eğer bir model kullanıyorsanız)
    reports = Report.objects.all()  # Tüm raporları alın
    return render(request, 'admin_dashboard/reports.html', {'reports': reports})
def approve_leave_request(request, pk):
    leave = get_object_or_404(Leave, pk=pk, status='pending')
    leave.status = 'approved'
    leave.save()

    # İlgili çalışanın bilgilerini alıyoruz
    employee = leave.user  # İzin isteyen çalışan
    remaining_days = employee.remaining_leave_days()  # Kalan izin günlerini hesapla
    if remaining_days < 3:
        Notification.objects.create(
            user=User.objects.filter(role='admin').first(),  # İlk yetkiliyi seçiyoruz
            message=f"{leave.user.username} has less than 3 leave days remaining."
        )
    messages.success(request, f"Leave request from {leave.start_date} to {leave.end_date} has been approved.")
    return redirect('admin-leave-requests')
def reject_leave_request(request, pk):
    leave = get_object_or_404(Leave, pk=pk, status='pending')
    leave.status = 'rejected'
    leave.save()
    messages.success(request, f"Leave request from {leave.start_date} to {leave.end_date} has been rejected.")
    return redirect('admin-leave-requests')
def create_leave(request):
    if request.user.role != 'admin':
        messages.error(request, "You are not authorized to create leaves.")
        return redirect('admin-dashboard')

    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        reason = request.POST.get('reason')

        employee = get_object_or_404(User, pk=employee_id, role='employee')

        if start_date and end_date:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()

            if start_date_obj > end_date_obj:
                messages.error(request, "Start date cannot be after end date.")
                return redirect('create-leave')

            Leave.objects.create(
                user=employee,
                start_date=start_date_obj,
                end_date=end_date_obj,
                reason=reason,
                status='approved'
            )
            # Kalan izin günlerini kontrol et
            remaining_days = employee.remaining_leave_days()
            if remaining_days < 3:
                Notification.objects.create(
                    user=User.objects.filter(role='admin').first(),  # İlk yetkiliyi seçiyoruz
                    message=f"{leave.user.username} has less than 3 leave days remaining."
                )
            messages.success(request, f"Leave created for {employee.username}.")
            return redirect('admin-leave-requests')
        else:
            messages.error(request, "Start date and end date are required.")

    employees = User.objects.filter(role='employee')
    return render(request, 'admin_dashboard/create_leave.html', {'employees': employees})
def detailed_work_report(request):
    if request.user.role != 'admin':
        messages.error(request, "You are not authorized to view this report.")
        return redirect('admin-dashboard')

    # Ay başlangıcı ve bitişi
    month = request.GET.get('month', datetime.now().strftime('%Y-%m'))  # Varsayılan olarak bu ay
    start_date = datetime.strptime(month, '%Y-%m').date()
    end_date = (start_date.replace(day=1) + timedelta(days=31)).replace(day=1) - timedelta(days=1)

    # İlgili ayın tüm giriş-çıkış kayıtlarını al
    work_data = Attendance.objects.filter(date__range=(start_date, end_date)).order_by('user__username', 'date')

    # Kullanıcı bazlı grup oluşturma
    grouped_work_data = {}
    for attendance in work_data:
        username = attendance.user.username
        if username not in grouped_work_data:
            grouped_work_data[username] = []
        
        # Çalışma süresini hesapla
        if attendance.checkin_time and attendance.checkout_time:
            checkin_datetime = datetime.combine(attendance.date, attendance.checkin_time)
            checkout_datetime = datetime.combine(attendance.date, attendance.checkout_time)
            work_duration = checkout_datetime - checkin_datetime
        else:
            work_duration = timedelta(0)

        grouped_work_data[username].append({
            'date': attendance.date,
            'work_duration': work_duration
        })

    return render(request, 'admin_dashboard/detailed_work_report.html', {
        'grouped_work_data': grouped_work_data,
        'month': month,
    })
def mark_notification_as_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('admin-dashboard')