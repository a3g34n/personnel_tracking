from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from datetime import timedelta, datetime, time

User = get_user_model()

class Attendance(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    checkin_time = models.TimeField(null=True, blank=True)
    checkout_time = models.TimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'date')  # Ensure one record per user per day

    def __str__(self):
        return f"{self.user.username} - {self.date}"

    @property
    def is_late(self):
        company_start_time = time(8, 0)  # 8:00 AM
        if self.checkin_time:
            return self.checkin_time > company_start_time
        return False
    @property
    def late_duration(self):
        company_start_time = time(8, 0)  # Şirketin giriş saati
        if self.checkin_time and self.checkin_time > company_start_time:
            checkin_datetime = datetime.combine(self.date, self.checkin_time)
            late_datetime = datetime.combine(self.date, company_start_time)
            return checkin_datetime - late_datetime  # Gecikme süresi (timedelta)
        return timedelta(0)
    @property
    def work_duration(self):
        """Günlük çalışma süresini hesaplar."""
        if self.checkin_time and self.checkout_time:
            checkin_datetime = datetime.combine(self.date, self.checkin_time)
            checkout_datetime = datetime.combine(self.date, self.checkout_time)
            return checkout_datetime - checkin_datetime
        return timedelta(0)