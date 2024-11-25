from django.urls import path
from .views import CheckinView, CheckoutView

urlpatterns = [
    path('checkin/', CheckinView.as_view(), name='checkin'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
]
