from rest_framework import serializers
from apps.employees.models import Designation, Department, Employee
from apps.employees.validators import (
    validate_age,
    validate_joining_date,
    validate_salary,
    validate_reporting_manager,
    validate_reporting_hierarchy,
    validate_department_head,
    validate_department_transfer,
    validate_status_transition
)


class EmployeeDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for Employee model.
    """
    class Meta:
        model = Employee
        fields = "__all__"
        read_only_fields = ("employee_code",)

class EmployeeCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating Employee instances.
    """
    class Meta:
        model = Employee
        fields = ("first_name", "last_name", "email", "phone_number", "date_of_birth", "profile_photo", "address",
                  "department", "designation", "reporting_to", "date_of_joining", "employment_type", "role", "salary")

    def validate(self, attrs):
        """
        Custom validations for employee creation.
        """
        validate_age(attrs.get("date_of_birth"), attrs.get("date_of_joining"))
        validate_joining_date(attrs.get("date_of_joining"))
        validate_salary(attrs.get("salary"))
        return attrs

class EmployeeUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating Employee instances.
    """
    class Meta:
        model = Employee
        fields = ("first_name", "last_name", "email", "phone_number", "profile_photo", "address",
                  "designation", "reporting_to", "employment_type", "role", "salary")

        read_only_fields = ("employee_code",)

    def validate(self, attrs):

        salary = attrs.get("salary", self.instance.salary)
        reporting_to = attrs.get("reporting_to", self.instance.reporting_to)
        
        validate_salary(salary)
        validate_reporting_manager(self.instance, reporting_to)
        validate_reporting_hierarchy(self.instance, reporting_to)

        return attrs

class EmployeeStatusSerializer(serializers.ModelSerializer):
    """
    Serializer for updating employee status.
    """
    class Meta:
        model = Employee
        fields = ("status")

    def validate(self, attrs):
        """
        Perform custom validations for employee status updates.
        """
        validate_status_transition(self.instance, attrs.get("status"))
        return attrs

class EmployeeTransferSerializer(serializers.ModelSerializer):
    """
    Serializer for transferring an employee to a different department.
    """
    class Meta:
        model = Employee
        fields = ("department")

    def validate(self, attrs):
        """
        Perform custom validations for employee transfer.
        """
        validate_department_transfer(self.instance, attrs.get("department"))
        return attrs

class DepartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department
        fields = ("name", "code", "head", "budget", "location", "is_active")

    def validate(self, attrs):
        head = attrs.get("head")

        if head is not None:
            validate_department_head(
                self.instance or Department(**attrs),
                head,
            )

        return attrs


class DesignationSerializer(serializers.ModelSerializer):
    """
    Serializer for Designation model.
    """
    class Meta:
        model = Designation
        fields = ("name", "description", "is_active")

    def validate(self, attrs):
        """
        Perform custom validations for designation updates.
        """
        # Add any custom validation logic for Designation here if needed
        return attrs