from django.db.models import Q

from apps.employees.choices import EmploymentRole
from apps.employees.models import Employee, Department


def get_accessible_employees(employee):
    """
    Return the employees that the given employee is allowed to access.
    """

    if employee.role in (
        EmploymentRole.ADMIN,
        EmploymentRole.HR,
    ):
        return Employee.objects.all()

    queryset = Employee.objects.none()

    if employee.role == EmploymentRole.MANAGER:
        queryset = Employee.objects.filter(
            reporting_to=employee,
        )

        headed_departments = employee.headed_departments.all()

        if headed_departments.exists():
            queryset = Employee.objects.filter(
                Q(reporting_to=employee)
                | Q(department__in=headed_departments)
            )

    elif employee.role == EmploymentRole.EMPLOYEE:
        queryset = Employee.objects.filter(
            id=employee.id,
        )

    return queryset.distinct()

def can_create_employee(employee):
    """
    Return whether the employee is allowed to create
    a new employee record.
    """

    return employee.role in (
        EmploymentRole.ADMIN,
        EmploymentRole.HR,
    )

def can_update_employee(employee, target_employee):
    """
    Return whether the employee is allowed to update
    the target employee record.
    """
    return target_employee in get_accessible_employees(employee)

def can_delete_employee(employee, target_employee):
    """
    Return whether the employee is allowed to soft delete
    the target employee record.
    """

    if employee.role in (
        EmploymentRole.ADMIN,
        EmploymentRole.HR,
    ):
        return True

    if employee.role == EmploymentRole.MANAGER:
        return target_employee.department_id in (
            employee.headed_departments.values_list(
                "id",
                flat=True,
            )
        )

    return False

def can_change_employee_status(employee, target_employee):
    """
    Return whether the employee is allowed to change
    the status of the target employee.
    """

    if employee.role in (
        EmploymentRole.ADMIN,
        EmploymentRole.HR,
    ):
        return True

    if employee.role == EmploymentRole.MANAGER:
        return target_employee.department_id in (
            employee.headed_departments.values_list(
                "id",
                flat=True,
            )
        )

    return False

ADMINISTRATION_DEPARTMENT_CODE = "ADM"


def is_administration_department(department):
    return department.code == ADMINISTRATION_DEPARTMENT_CODE


def get_accessible_departments(employee):
    """
    Return departments the employee is allowed to view.
    """

    if employee.role == EmploymentRole.ADMIN:
        return Department.objects.all()

    if employee.role == EmploymentRole.HR:
        return Department.objects.exclude(
            code=ADMINISTRATION_DEPARTMENT_CODE,
        )

    if employee.role == EmploymentRole.MANAGER:
        headed_departments = employee.headed_departments.all()

        if headed_departments.exists():
            return headed_departments

        return Department.objects.filter(
            manager=employee,
        )

    if employee.role == EmploymentRole.EMPLOYEE:
        return Department.objects.filter(
            id=employee.department_id,
        )

    return Department.objects.none()


def can_create_department(employee):
    return employee.role in (
        EmploymentRole.ADMIN,
        EmploymentRole.HR,
    )


def can_retrieve_department(employee, department):
    return get_accessible_departments(employee).filter(
        id=department.id,
    ).exists()


def can_update_department(
    employee,
    department,
    fields=None,
):
    """
    Return whether the employee may update the department.

    `fields` allows field-level authorization for sensitive
    organizational assignments.
    """

    if employee.role == EmploymentRole.ADMIN:
        return True

    if employee.role == EmploymentRole.HR:
        return not is_administration_department(department)

    if employee.role != EmploymentRole.MANAGER:
        return False

    if department.head_id != employee.id:
        return False

    if fields and "head" in fields:
        return False

    return True


def can_deactivate_department(employee, department):
    """
    Only Admin may deactivate departments.
    """

    return employee.role == EmploymentRole.ADMIN