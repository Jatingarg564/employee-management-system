from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers

from apps.employees.models import (
    Department,
    Designation,
    Employee,
)

from apps.employees.validators import (
    validate_age,
    validate_department_head,
    validate_department_transfer,
    validate_joining_date,
    validate_reporting_hierarchy,
    validate_reporting_manager,
    validate_salary,
    validate_status_transition,
)


class EmployeeDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for Employee model.
    """
    class Meta:
        model = Employee
        fields = (
            "id",
            "employee_code",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "date_of_birth",
            "department",
            "designation",
            "reporting_to",
            "date_of_joining",
            "employment_type",
            "role",
            "status",
            "salary",
            "profile_photo",
            "address",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "employee_code",
            "created_at",
            "updated_at",
        )

class EmployeeCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating Employee instances.
    """

    username = serializers.CharField(max_length=150)
    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )

    class Meta:
        model = Employee
        fields = (
            "username",
            "password",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "date_of_birth",
            "profile_photo",
            "address",
            "department",
            "designation",
            "reporting_to",
            "date_of_joining",
            "employment_type",
            "role",
            "salary",
        )

    def validate(self, attrs):
        """
        Perform custom validations for employee creation.
        """

        validate_age(
            attrs["date_of_birth"],
            attrs["date_of_joining"],
        )

        validate_joining_date(
            attrs["date_of_joining"],
        )

        validate_salary(
            attrs["salary"],
        )

        validate_password(
            password=attrs["password"],
        )

        if User.objects.filter(
            username=attrs["username"]
        ).exists():
            raise serializers.ValidationError(
                {
                    "username":
                    "A user with this username already exists."
                }
            )

        return attrs

class EmployeeUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating employee information.
    """

    class Meta:
        model = Employee
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "profile_photo",
            "address",
            "designation",
            "reporting_to",
            "employment_type",
            "role",
            "salary",
        )

        read_only_fields = (
            "employee_code",
        )

    def validate(self, attrs):
        """
        Perform custom validations for employee updates.
        """

        salary = attrs.get(
            "salary",
            self.instance.salary if self.instance else None,
        )

        reporting_to = attrs.get(
            "reporting_to",
            self.instance.reporting_to if self.instance else None,
        )

        validate_salary(salary)

        validate_reporting_manager(
            self.instance,
            reporting_to,
        )

        validate_reporting_hierarchy(
            self.instance,
            reporting_to,
        )

        return attrs

class EmployeeStatusSerializer(serializers.ModelSerializer):
    """
    Serializer for updating employee status.
    """
    class Meta:
        model = Employee
        fields = (
            "status",
        )

    def validate(self, attrs):
        """
        Perform custom validations for employee status updates.
        """
        validate_status_transition(self.instance, attrs["status"])
        return attrs

class EmployeeTransferSerializer(serializers.ModelSerializer):
    """
    Serializer for transferring an employee to a different department.
    """
    class Meta:
        model = Employee
        fields = (
            "department",
        )

    def validate(self, attrs):
        """
        Perform custom validations for employee transfer.
        """
        validate_department_transfer(self.instance, attrs["department"])
        return attrs

class DepartmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Department
        fields = (
            "name", 
            "code", 
            "head", 
            "budget", 
            "location", 
            "is_active"
        )

    def validate(self, attrs):
        """
        Perform custom validations for department creation and updates.
        """

        department = self.instance or Department(**attrs)

        head = attrs.get(
            "head",
            department.head,
        )

        validate_department_head(
            department,
            head,
        )

        return attrs


class DesignationSerializer(serializers.ModelSerializer):
    """
    Serializer for Designation model.
    """
    class Meta:
        model = Designation
        fields = (
            "name", 
            "description", 
            "is_active"
        )

    def validate(self, attrs):
        """
        Perform custom validations for designation updates.
        """

        return attrs