# Python imajını seçiyoruz
FROM python:3.10-slim

# Çalışma dizinini belirtiyoruz
WORKDIR /app

# Gereksinim dosyasını kopyalıyoruz
COPY requirements.txt .

RUN python -m pip install --upgrade pip
# Gerekli bağımlılıkları kuruyoruz
RUN pip install --no-cache-dir -r requirements.txt --timeout 120 --retries 5

# Proje dosyalarını kopyalıyoruz
COPY . .

# Django sunucusunu çalıştırma komutunu veriyoruz
CMD ["sh", "-c", "python manage.py migrate && python manage.py runscript create_superuser && python manage.py runserver 0.0.0.0:8000"]

