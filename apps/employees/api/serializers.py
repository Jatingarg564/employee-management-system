import attrs
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from apps.employees.choices import EmploymentRole
from apps.employees.models import (
    Department,
    Designation,
    Employee,
)

from apps.employees.validators import (
    validate_age,
    validate_department_budget,
    validate_department_leadership_employee,
    validate_department_leadership_integrity,
    validate_department_head,
    validate_department_manager,
    validate_department_transfer,
    validate_email_uniqueness,
    validate_joining_date,
    validate_profile_photo,
    validate_reporting_hierarchy,
    validate_reporting_manager,
    validate_salary,
    validate_status_transition,
    validate_username_uniqueness,
)


class EmployeeDetailSerializer(serializers.ModelSerializer):
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
        )

        read_only_fields = (
            "employee_code",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)

        request = self.context.get("request")

        if not request:
            return data

        viewer = getattr(
            request.user,
            "employee_profile",
            None,
        )

        if not viewer:
            return data

        if (
            viewer.role == EmploymentRole.MANAGER
            and instance != viewer
        ):
            data.pop("date_of_birth", None)
            data.pop("address", None)
            data.pop("salary", None)

        return data


class EmployeeCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating Employee instances.
    """

    username = serializers.CharField(max_length=150)

    role = serializers.ChoiceField(
        choices=EmploymentRole.choices,
        required=True,
        allow_null=False,
    )

    class Meta:
        model = Employee
        fields = (
            "username",
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

        if "profile_photo" in attrs:
            attrs["profile_photo"] = validate_profile_photo(
                attrs["profile_photo"],
            )

        return attrs


class EmployeeUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating employee information.
    """

    profile_photo = serializers.ImageField(
        required=False,
        allow_null=True,
    )

    remove_profile_photo = serializers.BooleanField(
        required=False,
        write_only=True,
        default=False,
    )

    class Meta:
        model = Employee
        fields = (
            "first_name",
            "last_name",
            "phone_number",
            "date_of_birth",
            "profile_photo",
            "remove_profile_photo",
            "address",
            "department",
            "designation",
            "reporting_to",
            "date_of_joining",
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

        remove_profile_photo = attrs.pop(
            "remove_profile_photo",
            False,
        )

        if remove_profile_photo:
            attrs["profile_photo"] = None

        salary = attrs.get(
            "salary",
            self.instance.salary,
        )

        reporting_to = attrs.get(
            "reporting_to",
            self.instance.reporting_to,
        )

        new_role = attrs.get(
            "role",
            self.instance.role,
        )

        date_of_birth = attrs.get(
            "date_of_birth",
            self.instance.date_of_birth,
        )

        date_of_joining = attrs.get(
            "date_of_joining",
            self.instance.date_of_joining,
        )

        validate_salary(
            salary,
        )

        validate_joining_date(
            date_of_joining,
        )

        validate_age(
            date_of_birth,
            date_of_joining,
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

        validate_department_leadership_integrity(
            employee=self.instance,
            new_role=new_role,
        )

        if (
            "profile_photo" in attrs
            and attrs["profile_photo"] is not None
        ):
            attrs["profile_photo"] = validate_profile_photo(
                attrs["profile_photo"],
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
            "is_active",
            "created_at",
            "updated_at",
        )

    def validate(self, attrs):

        manager = attrs.get(
            "manager",
            self.instance.manager if self.instance else None,
        )

        head = attrs.get(
            "head",
            self.instance.head if self.instance else None,
        )

        budget = attrs.get(
            "budget",
            self.instance.budget if self.instance else 0,
        )

        validate_department_manager(
            manager,
        )

        validate_department_head(
            head,
        )

        validate_department_budget(
            budget,
        )

        return attrs


class EmployeeDepartmentSerializer(serializers.ModelSerializer):
    manager = serializers.SerializerMethodField()
    head = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = (
            "id",
            "name",
            "code",
            "manager",
            "head",
        )

    def get_manager(self, obj):
        if obj.manager is None:
            return None

        return (
            f"{obj.manager.first_name} "
            f"{obj.manager.last_name}"
        )

    def get_head(self, obj):
        if obj.head is None:
            return None

        return (
            f"{obj.head.first_name} "
            f"{obj.head.last_name}"
        )


class DesignationSerializer(serializers.ModelSerializer):
    """
    Serializer for Designation model.
    """

    class Meta:
        model = Designation
        fields = (
            "id",
            "name",
            "description",
            "is_active",
        )

    def validate(self, attrs):
        """
        Perform custom validations for designation updates.
        """

        return attrs
    
    
