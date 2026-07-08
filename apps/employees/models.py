from django.db import models
from django.contrib.auth.models import User
from apps.employees.choices import EmploymentType, EmploymentRole, EmployeeStatus


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    head = models.ForeignKey("Employee", on_delete=models.SET_NULL, null=True, blank=True, related_name="headed_departments")
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    location = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Designation(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="employee_profile")
    employee_code = models.CharField(max_length=20, unique=True)

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField()

    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="employees")
    designation = models.ForeignKey(Designation, on_delete=models.PROTECT, related_name="employees")
    reporting_to = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="subordinates")
    date_of_joining = models.DateField()
    employment_type = models.CharField(max_length=2, choices=EmploymentType.choices)
    role = models.CharField(max_length=2, choices=EmploymentRole.choices, default=EmploymentRole.EMPLOYEE)
    status = models.CharField(max_length=2, choices=EmployeeStatus.choices, default=EmployeeStatus.ACTIVE)

    salary = models.DecimalField(max_digits=10, decimal_places=2)

    profile_photo = models.ImageField(upload_to="employee_profiles/", null=True, blank=True)
    address = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee_code} - {self.first_name} {self.last_name}"