from django.db.models import Q

from apps.employees.choices import EmploymentRole
from apps.employees.models import Employee


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