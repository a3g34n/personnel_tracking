from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Count
from attendance.models import Attendance
from leave_management.models import Leave
from personnel.models import User
from datetime import timedelta

class MonthlyReportView(APIView):
    def get(self, request, month, year):
        # Tüm çalışanları döndür
        employees = User.objects.filter(role='employee')
        report_data = []

        for employee in employees:
            # Çalışma sürelerini hesapla
            attendance_records = Attendance.objects.filter(
                user=employee,
                date__month=month,
                date__year=year,
                checkout_time__isnull=False  # Çıkış yapmış olanlar
            )

            total_work_seconds = sum(
                (timedelta(hours=rec.checkout_time.hour, minutes=rec.checkout_time.minute) -
                 timedelta(hours=rec.checkin_time.hour, minutes=rec.checkin_time.minute)).total_seconds()
                for rec in attendance_records
            )
            total_work_hours = total_work_seconds / 3600

            # Geç kalma günlerini hesapla
            total_late_days = attendance_records.filter(
                checkin_time__gt='08:00:00'  # Şirketin giriş saati
            ).count()

            # Kullanılan izinleri hesapla
            total_leave_days = Leave.objects.filter(
                user=employee,
                start_date__month=month,
                start_date__year=year,
                status='approved'
            ).aggregate(total_days=Sum('leave_days'))['total_days'] or 0

            report_data.append({
                'user': employee.username,
                'total_work_hours': total_work_hours,
                'total_late_days': total_late_days,
                'total_leave_days': total_leave_days,
            })

        return Response(report_data)
