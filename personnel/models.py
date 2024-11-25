from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Sum
from datetime import timedelta
from django.db.models import Sum, F, ExpressionWrapper, DurationField

class User(AbstractUser):
    ROLE_CHOICES = (
        ('employee', 'Employee'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='employee')
    leave_entitlement = models.IntegerField(default=15)  # Varsayılan izin hakkı 15 gün
    phone_number = models.CharField(max_length=15, null=True, blank=True)  # Telefon numarası
    date_of_birth = models.DateField(null=True, blank=True)  # Doğum tarihi
    
    def __str__(self):
        return self.username
    
    def remaining_leave_days(self):
        # Onaylanmış izinlerin toplamını hesapla
        approved_leaves = self.leave_set.filter(status='approved').aggregate(
            total_days=Sum(F('end_date') - F('start_date'))
        )['total_days'] or timedelta(0)
        return self.leave_entitlement - approved_leaves.days
