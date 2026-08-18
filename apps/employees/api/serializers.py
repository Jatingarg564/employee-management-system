from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.employees.models import (
    Department,
    Designation,
    Employee,
)

from apps.employees.validators import (
    validate_age,
    validate_department_leadership_employee,
    validate_department_transfer,
    validate_email_uniqueness,
    validate_joining_date,
    validate_reporting_hierarchy,
    validate_reporting_manager,
    validate_salary,
    validate_status_transition,
    validate_username_uniqueness,
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

        validate_email_uniqueness(
            employee=None,
            email=attrs["email"],
        )

        validate_username_uniqueness(
            user=None,
            username=attrs["username"],
        )

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
            "phone_number",
            "profile_photo",
            "address",
            "department",
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
            self.instance.salary,
        )

        reporting_to = attrs.get(
            "reporting_to",
            self.instance.reporting_to,
        )

        validate_salary(
            salary,
        )

        if "department" in attrs:
            validate_department_transfer(
                self.instance,
                attrs["department"],
            )

        validate_reporting_manager(
            self.instance,
            reporting_to,
        )

        validate_reporting_hierarchy(
            self.instance,
            reporting_to,
        )

        return attrs

class EmployeeStatusUpdateSerializer(serializers.ModelSerializer):
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

        validate_status_transition(
            self.instance,
            attrs["status"],
        )

        return attrs


class DepartmentSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating Department instances.
    """

    class Meta:
        model = Department

        fields = (
            "id",
            "name",
            "code",
            "manager",
            "head",
            "budget",
            "location",
            "is_active",
            "created_at",
            "updated_at",
        )

        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )

    def validate(self, attrs):
        """
        Validate department manager and head assignments.
        """

        manager = attrs.get(
            "manager",
            self.instance.manager if self.instance else None,
        )

        head = attrs.get(
            "head",
            self.instance.head if self.instance else None,
        )

        validate_department_leadership_employee(
            manager,
        )

        validate_department_leadership_employee(
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
            "is_active",
        )

    def validate(self, attrs):
        """
        Perform custom validations for designation updates.
        """

        return attrs
    
    