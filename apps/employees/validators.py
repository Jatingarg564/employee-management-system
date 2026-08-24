from django.utils import timezone

from dateutil.relativedelta import relativedelta

from django.contrib.auth.models import User

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.employees.choices import (
    EmployeeStatus,
    EmploymentRole,
)

from apps.employees.models import Employee


# ============================================================
# EMPLOYEE UNIQUENESS VALIDATIONS
# ============================================================

def validate_email_uniqueness(employee, email):
    """
    Validate that the email is unique across all employees.
    """

    employees = Employee.objects.filter(
        email=email,
    )

    if employee is not None:
        employees = employees.exclude(
            id=employee.id,
        )

    if employees.exists():
        raise ValidationError(
            "An employee with this email already exists."
        )


def validate_username_uniqueness(user, username):
    """
    Validate that the username is unique across all users.
    """

    users = User.objects.filter(
        username=username,
    )

    if user is not None:
        users = users.exclude(
            id=user.id,
        )

    if users.exists():
        raise ValidationError(
            "A user with this username already exists."
        )


# ============================================================
# EMPLOYEE PERSONAL AND EMPLOYMENT VALIDATIONS
# ============================================================

def validate_age(date_of_birth, date_of_joining):
    """
    Validate that the employee is at least 18 years old
    on the date of joining.
    """

    cutoff_date = date_of_joining - relativedelta(
        years=18,
    )

    if date_of_birth > cutoff_date:
        raise ValidationError(
            "Employee must be at least 18 years old "
            "at the time of joining."
        )


def validate_joining_date(date_of_joining):
    """
    Validate that the joining date is not in the future.
    """

    if date_of_joining > timezone.now().date():
        raise ValidationError(
            "Joining date cannot be in the future."
        )


def validate_salary(salary):
    """
    Validate that salary is greater than zero.
    """

    if salary <= 0:
        raise ValidationError(
            "Salary must be greater than zero."
        )


# ============================================================
# EMPLOYEE REPORTING HIERARCHY VALIDATIONS
# ============================================================

def validate_reporting_manager(employee, reporting_to):
    """
    Validate that an employee cannot report to themselves.
    """

    if (
        reporting_to is not None
        and employee == reporting_to
    ):
        raise ValidationError(
            "An employee cannot report to themselves."
        )


def validate_reporting_hierarchy(employee, reporting_to):
    """
    Validate that an employee cannot report to one of their
    own subordinates.

    This prevents circular reporting relationships.
    """

    if reporting_to is None:
        return

    current_manager = reporting_to

    while current_manager is not None:

        if current_manager == employee:
            raise ValidationError(
                "An employee cannot report to their subordinates."
            )

        current_manager = current_manager.reporting_to


# ============================================================
# DEPARTMENT LEADERSHIP VALIDATIONS
# ============================================================

def validate_department_leadership_employee(employee):
    """
    Validate whether an employee is eligible for a department
    leadership responsibility.

    A department manager or department head must:

    - Have the MANAGER role.
    - Have ACTIVE employment status.

    The employee's primary department does not determine
    eligibility for leadership responsibility.
    """

    if employee is None:
        return

    if employee.role != EmploymentRole.MANAGER:
        raise ValidationError(
            "Only an employee with the MANAGER role can be "
            "assigned to a department leadership position."
        )

    if employee.status != EmployeeStatus.ACTIVE:
        raise ValidationError(
            "Only an active employee can be assigned to a "
            "department leadership position."
        )

def validate_department_budget(budget):
    """
    Validate that a department budget is not negative.
    """

    if budget < 0:
        raise ValidationError(
            "Department budget cannot be negative."
        )

def validate_department_manager(manager):
    """
    Validate whether an employee is eligible to be assigned
    as the operational manager of a department.
    """

    validate_department_leadership_employee(
        manager,
    )


def validate_department_head(head):
    """
    Validate whether an employee is eligible to be assigned
    as the Head of Department (HOD).
    """

    validate_department_leadership_employee(
        head,
    )


def validate_department_leadership_integrity(
    employee,
    new_role=None,
    new_status=None,
):
    """
    Ensure that changes to an employee do not invalidate
    existing department leadership responsibilities.

    An employee can be:

    - Manager of one or more departments.
    - Head of one or more departments.

    Business Rules:

    - Department managers must retain the MANAGER role.
    - Department heads must retain the MANAGER role.
    - Department managers must remain ACTIVE.
    - Department heads must remain ACTIVE.
    - Changing the employee's primary department does not
      affect their leadership responsibilities.
    """

    managed_departments = (
        employee.managed_departments.all()
    )

    headed_departments = (
        employee.headed_departments.all()
    )

    has_leadership_responsibility = (
        managed_departments.exists()
        or headed_departments.exists()
    )

    if not has_leadership_responsibility:
        return

    if (
        new_role is not None
        and new_role != EmploymentRole.MANAGER
    ):
        raise ValidationError(
            "An employee assigned as a department manager or "
            "department head must retain the MANAGER role."
        )

    if (
        new_status is not None
        and new_status != EmployeeStatus.ACTIVE
    ):
        raise ValidationError(
            "An employee assigned as a department manager or "
            "department head must remain ACTIVE."
        )


# ============================================================
# DEPARTMENT TRANSFER VALIDATIONS
# ============================================================

def validate_department_transfer(
    employee,
    new_department,
):
    """
    Validate that an employee can be transferred to another
    department.
    """

    if employee.status in [
        EmployeeStatus.RESIGNED,
        EmployeeStatus.TERMINATED,
    ]:
        raise ValidationError(
            "Resigned or terminated employees cannot be "
            "transferred to another department."
        )

    if employee.department == new_department:
        raise serializers.ValidationError(
            {
                "department": (
                    "Employee is already assigned to this department."
                )
            }
        )


# ============================================================
# EMPLOYEE STATUS TRANSITION VALIDATIONS
# ============================================================

def validate_status_transition(
    employee,
    new_status,
):
    """
    Validate that the employee status transition is allowed.

    Business Rules:

    ACTIVE:
        → INACTIVE
        → ON_LEAVE
        → TERMINATED
        → RESIGNED

    INACTIVE:
        → ACTIVE
        → ON_LEAVE
        → TERMINATED
        → RESIGNED

    ON_LEAVE:
        → ACTIVE
        → INACTIVE
        → TERMINATED
        → RESIGNED

    RESIGNED:
        → ACTIVE within 30 days

    TERMINATED:
        → No transitions allowed
    """

    old_status = employee.status

    valid_transitions = {
        EmployeeStatus.ACTIVE: [
            EmployeeStatus.INACTIVE,
            EmployeeStatus.ON_LEAVE,
            EmployeeStatus.TERMINATED,
            EmployeeStatus.RESIGNED,
        ],

        EmployeeStatus.INACTIVE: [
            EmployeeStatus.ACTIVE,
            EmployeeStatus.ON_LEAVE,
            EmployeeStatus.TERMINATED,
            EmployeeStatus.RESIGNED,
        ],

        EmployeeStatus.ON_LEAVE: [
            EmployeeStatus.ACTIVE,
            EmployeeStatus.INACTIVE,
            EmployeeStatus.TERMINATED,
            EmployeeStatus.RESIGNED,
        ],

        EmployeeStatus.RESIGNED: [
            EmployeeStatus.ACTIVE,
        ],

        EmployeeStatus.TERMINATED: [],
    }

    if new_status not in valid_transitions.get(
        old_status,
        [],
    ):
        raise ValidationError(
            f"Invalid status transition from "
            f"{old_status} to {new_status}."
        )

    if (
        old_status == EmployeeStatus.RESIGNED
        and new_status == EmployeeStatus.ACTIVE
    ):

        if employee.resignation_date is None:
            raise ValidationError(
                "Resignation date is missing for this employee."
            )

        today = timezone.now().date()

        days_since_resignation = (
            today - employee.resignation_date
        ).days

        if days_since_resignation > 30:
            raise ValidationError(
                "A resigned employee can only be reactivated "
                "within 30 days of resignation."
            )
    