from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Leave
from .serializers import LeaveSerializer
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from notifications.models import Notification
from personnel.models import User  # Kullanıcı modeli
from notifications.models import Notification
from personnel.models import User
from django.contrib.auth import get_user_model

User = get_user_model()

class LeaveRequestView(APIView):
    @method_decorator(login_required)
    def post(self, request):
        serializer = LeaveSerializer(data=request.data)
        if serializer.is_valid():
            leave = serializer.save(user=request.user)

            # Yetkiliye bildirim gönder
            admin_users = User.objects.filter(role='admin')
            for admin in admin_users:
                Notification.objects.create(
                    user=admin,
                    message=f"{request.user.username} has requested leave from {leave.start_date} to {leave.end_date}."
                )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LeaveListView(APIView):
    @method_decorator(login_required)
    def get(self, request):
        leaves = Leave.objects.filter(user=request.user)
        serializer = LeaveSerializer(leaves, many=True)
        return Response(serializer.data)

class LeaveApprovalView(APIView):
    @method_decorator(login_required)
    def patch(self, request, pk):
        try:
            leave = Leave.objects.get(pk=pk, status='pending')
            if request.user.role != 'admin':
                return Response({"error": "Only admins can approve or reject leaves."}, status=status.HTTP_403_FORBIDDEN)

            status_action = request.data.get('status')
            if status_action == 'approved':
                leave.status = 'approved'
                leave.save()
                return Response({"message": "Leave request approved."}, status=status.HTTP_200_OK)
            elif status_action == 'rejected':
                leave.status = 'rejected'
                leave.save()
                return Response({"message": "Leave request rejected."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid status action."}, status=status.HTTP_400_BAD_REQUEST)
        except Leave.DoesNotExist:
            return Response({"error": "Leave request not found or already processed."}, status=status.HTTP_404_NOT_FOUND)

