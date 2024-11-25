from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Attendance
from datetime import datetime
from notifications.models import Notification
from django.contrib.auth import get_user_model
from personnel.models import User

User = get_user_model()

class CheckinView(APIView):
    def post(self, request):
        user = request.user
        today = datetime.now().date()

        # Günlük giriş kaydı kontrolü
        attendance, created = Attendance.objects.get_or_create(user=user, date=today)
        if not attendance.checkin_time:          
            # Giriş zamanını kaydet
            attendance.checkin_time = datetime.now().time()
            attendance.save()

        if attendance.is_late:
            late_duration = attendance.late_duration  # Geç kalınan süre (timedelta)
            late_minutes = late_duration.total_seconds() / 60  # Geç kalınan süreyi dakikaya çevir

            # Geç kalma süresini yıllık izinden düşme
            late_days = late_minutes / (8 * 60)  # Bir iş günü 8 saat olarak hesaplanır
            user.leave_entitlement -= late_days
            user.save()
            
            Notification.objects.create(
                user=User.objects.filter(role='admin').first(),  # İlk yetkiliyi seçiyoruz
                message=f"{user.username} has checked in late at {attendance.checkin_time}."
            )

        return Response({"message": "Check-in successful!"}, status=status.HTTP_200_OK)

class CheckoutView(APIView):
    def post(self, request):
        user = request.user
        today = datetime.now().date()

        try:
            attendance = Attendance.objects.get(user=user, date=today)
            
            # Çıkış zamanını kaydet
            attendance.checkout_time = datetime.now().time()
            attendance.save()
            return Response({"message": "Check-out successful!"}, status=status.HTTP_200_OK)
        except Attendance.DoesNotExist:
            return Response({"message": "No check-in record found for today."}, status=status.HTTP_400_BAD_REQUEST)
