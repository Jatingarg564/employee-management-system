from rest_framework import serializers
from apps.employees.models import Employee


class EmployeeSerializer(serializers.ModelSerializer):
    """
    Serializer for Employee model.
    """

    class Meta:
        model = Employee
        fields = "__all__"
        read_only_fields = ("employee_code",)