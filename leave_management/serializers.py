from rest_framework import serializers
from .models import Leave

class LeaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leave
        fields = ['id', 'user', 'start_date', 'end_date', 'reason', 'status', 'leave_days', 'created_at']
        read_only_fields = ['status', 'leave_days', 'created_at']
