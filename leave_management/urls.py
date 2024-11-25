from django.urls import path
from .views import LeaveRequestView, LeaveListView, LeaveApprovalView

urlpatterns = [
    path('request/', LeaveRequestView.as_view(), name='leave_request'),
    path('list/', LeaveListView.as_view(), name='leave_list'),
    path('<int:pk>/approve/', LeaveApprovalView.as_view(), name='leave_approval'),
]
