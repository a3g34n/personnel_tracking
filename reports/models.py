from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Report(models.Model):
    name = models.CharField(max_length=255)  # Rapor adı
    description = models.TextField(null=True, blank=True)  # Rapor açıklaması
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)  # Raporu oluşturan kişi
    created_at = models.DateTimeField(auto_now_add=True)  # Rapor oluşturulma zamanı

    def __str__(self):
        return self.name
