from rest_framework import serializers

class EmployeeReportSerializer(serializers.Serializer):
    user = serializers.CharField()
    total_work_hours = serializers.FloatField()
    total_late_days = serializers.IntegerField()
    total_leave_days = serializers.IntegerField()
