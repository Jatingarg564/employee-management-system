from django.core.exceptions import ValidationError
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from apps.employees.choices import EmployeeStatus


def validate_age(date_of_birth, date_of_joining):
    """
    Validate that the employee is at least 18 years old
    on the date of joining.
    """
    cutoff_date = date_of_joining - relativedelta(years=18)

    if date_of_birth > cutoff_date:
        raise ValidationError(
            "Employee must be at least 18 years old at the time of joining."
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


def validate_reporting_manager(employee, reporting_to):
    """
    Validate that an employee cannot report to themselves.
    """
    if reporting_to is not None and employee == reporting_to:
        raise ValidationError(
            "An employee cannot report to themselves."
        )


def validate_reporting_hierarchy(employee, reporting_to):
    """
    Validate that an employee cannot report to their subordinates.
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


def validate_department_head(department, head):
    """
    Validate that the department head belongs to the same department
    and is eligible to be assigned as the department head.
    """
    if head is None:
        return

    if head.department != department:
        raise ValidationError(
            "The department head must belong to the same department."
        )

    if head.status in [
        EmployeeStatus.INACTIVE,
        EmployeeStatus.RESIGNED,
        EmployeeStatus.TERMINATED,
    ]:
        raise ValidationError(
            "An inactive, resigned, or terminated employee cannot be assigned as the department head."
        )


def validate_department_transfer(employee, new_department):
    """
    Validate that an employee can be transferred to another department.
    """
    if employee.status in [
        EmployeeStatus.RESIGNED,
        EmployeeStatus.TERMINATED,
    ]:
        raise ValidationError(
            "Resigned or terminated employees cannot be transferred to another department."
        )

    if employee.department == new_department:
        raise ValidationError(
            "Employee is already assigned to this department."
        )


def validate_status_transition(employee, new_status):
    """
    Validate that the employee status transition is allowed.

    Business Rules:
    - ACTIVE → INACTIVE / ON_LEAVE / TERMINATED / RESIGNED
    - INACTIVE → ACTIVE / ON_LEAVE / TERMINATED / RESIGNED
    - ON_LEAVE → ACTIVE / INACTIVE / TERMINATED / RESIGNED
    - RESIGNED → ACTIVE (only within 30 days)
    - TERMINATED → No transitions allowed
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

    if new_status not in valid_transitions.get(old_status, []):
        raise ValidationError(
            f"Invalid status transition from {old_status} to {new_status}."
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
                "A resigned employee can only be reactivated within 30 days of resignation."
            )
        