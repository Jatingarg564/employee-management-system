from django.db import models
from django.contrib.auth.models import User

from apps.employees.choices import( 
    EmploymentType, 
    EmploymentRole, 
    EmployeeStatus
)

from django.db import models


from django.db import models


class Department(models.Model):
    """
    Represents an organizational department.

    Each department can have:
    - One operational manager
    - One department head / HOD

    A manager or HOD can be responsible for multiple departments.
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
    )

    code = models.CharField(
        max_length=10,
        unique=True,
        db_index=True,
    )

    manager = models.ForeignKey(
        "Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_departments",
        help_text="Employee responsible for the day-to-day management of this department.",
    )

    head = models.ForeignKey(
        "Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="headed_departments",
        help_text="Employee responsible for overall leadership of this department.",
    )

    budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    location = models.CharField(
        max_length=200,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
    )

    class Meta:
        ordering = (
            "name",
    )

        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    budget__gte=0,
                ),
                name="department_budget_non_negative",
            ),
        ]

        verbose_name = "Department"
        verbose_name_plural = "Departments"

    def __str__(self):
        return f"{self.name} ({self.code})"
class Designation(models.Model):
    name = models.CharField(
        max_length=100, 
        unique=True
    )
    
    description = models.TextField(
        blank=True
    )
    
    is_active = models.BooleanField(
        default=True
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.name


class Employee(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="employee_profile"
    )

    employee_code = models.CharField(
        max_length=20,
        unique=True
    )

    first_name = models.CharField(
        max_length=100
    )

    last_name = models.CharField(
        max_length=100
    )

    email = models.EmailField(
        unique=True
    )

    phone_number = models.CharField(
        max_length=15,
        unique=True
    )

    date_of_birth = models.DateField()

    department = models.ForeignKey(
        Department, 
        on_delete=models.PROTECT, 
        related_name="employees"
    )
    
    designation = models.ForeignKey(
        Designation, 
        on_delete=models.PROTECT, 
        related_name="employees"
    )
    
    reporting_to = models.ForeignKey(
        "self", 
        on_delete=models.SET_NULL, 
        null=True, blank=True, 
        related_name="subordinates"
    )
    
    date_of_joining = models.DateField()

    employment_type = models.CharField(
        max_length=2, 
        choices=EmploymentType.choices
    )
    role = models.CharField(
        max_length=2, 
        choices=EmploymentRole.choices, 
        default=EmploymentRole.EMPLOYEE
    )
    
    status = models.CharField(
        max_length=2, 
        choices=EmployeeStatus.choices, 
        default=EmployeeStatus.ACTIVE
    )
    
    resignation_date = models.DateField(
        null=True, 
        blank=True
    )
    
    termination_date = models.DateField(
        null=True, 
        blank=True
    )

    salary = models.DecimalField(
        max_digits=10, 
        decimal_places=2
    )

    profile_photo = models.ImageField(
        upload_to="employee_profiles/", 
        null=True, 
        blank=True
    )

    address = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.employee_code} - {self.first_name} {self.last_name}"