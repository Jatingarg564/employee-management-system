from django.core.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from django.utils import timezone


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

def validate_reporting_manager(employee,reporting_to):
    