from django.urls import path
from .views import MonthlyReportView

urlpatterns = [
    path('<int:year>/<int:month>/', MonthlyReportView.as_view(), name='monthly_report'),
]
