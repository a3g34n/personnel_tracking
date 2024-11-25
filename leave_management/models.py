from django.db import models
from django.conf import settings

class Leave(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.status}"

    @property
    def leave_days(self):
        # İzin günlerini hesaplama
        return (self.end_date - self.start_date).days + 1

    @staticmethod
    def remaining_leave_days(user):
        # Kullanıcının kalan izin günlerini hesaplar
        total_entitlement = user.leave_entitlement
        approved_leaves = Leave.objects.filter(user=user, status='approved')
        used_leave_days = sum(leave.leave_days for leave in approved_leaves)
        return total_entitlement - used_leave_days