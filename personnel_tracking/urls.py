"""
URL configuration for personnel_tracking project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views
from personnel.views import custom_logout

urlpatterns = [
    path('logout/', custom_logout, name='logout'),  
    path('admin/', include('admin_dashboard.urls')),
    path('employee/', include('employee_dashboard.urls')),
    path('api/attendance/', include('attendance.urls')),
    path('api/leaves/', include('leave_management.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/reports/', include('reports.urls')),
]