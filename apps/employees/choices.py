from django.db import models

class EmploymentType(models.TextChoices):
    FULL_TIME = 'FT', 'Full Time'
    PART_TIME = 'PT', 'Part Time'
    CONTRACT = 'CT', 'Contract'
    INTERN = 'IN', 'Intern'

class EmploymentStatus(models.TextChoices):
    ACTIVE = 'AC', 'Active'
    INACTIVE = 'IN', 'Inactive'
    ON_LEAVE = 'OL', 'On Leave'
    TERMINATED = 'TE', 'Terminated'
    RESIGNED = 'RE', 'Resigned'

class EmploymentRole(models.TextChoices):
    ADMIN = 'AD', 'Admin'
    HR = 'HR', 'HR'
    MANAGER = 'MG', 'Manager'
    EMPLOYEE = 'EM', 'Employee'