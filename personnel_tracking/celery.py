from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Django ayarlarını varsayılan olarak ayarla
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'personnel_tracking.settings')

app = Celery('personnel_tracking')

# Ayarları Django'nun settings.py dosyasından al
app.config_from_object('django.conf:settings', namespace='CELERY')

# Tüm uygulamalardan görevleri otomatik olarak bul
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
