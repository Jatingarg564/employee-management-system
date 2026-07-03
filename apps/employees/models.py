from django.db import models
from apps.employees.choices import EmploymentType, EmploymentRole, EmployeeStatus

# Create your models here.
class Department(models.Model):
    """ Represents a department within the organization. """

    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class Designation(models.Model):
    """ Represents an organizational designation/job title. """

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Employee(models.Model):
    """ Represents an employee in the organization. """

    #Personal Details
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, unique=True)
    date_of_birth = models.DateField()

    #Professional Details
    employee_code = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='employees')
    designation = models.ForeignKey(Designation, on_delete=models.PROTECT, related_name="employees",)
    date_of_joining = models.DateField()
    employment_type = models.CharField(max_length=2, choices=EmploymentType.choices)
    role = models.CharField(max_length=2, choices=EmploymentRole.choices)
    status = models.CharField(max_length=2, choices=EmployeeStatus.choices, default=EmployeeStatus.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    #Compensation Details
    salary = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

