from django.urls import path

from apps.employees.api.views import (
    DepartmentListCreateAPIView,
    DepartmentRetrieveUpdateDestroyAPIView,
    EmployeeListCreateAPIView,
    EmployeeRetrieveUpdateDestroyAPIView,
    EmployeeStatusAPIView,
)

urlpatterns = [

    # Employees
    path(
        "",
        EmployeeListCreateAPIView.as_view(),
        name="employee-list-create",
    ),

    path(
        "<int:employee_id>/",
        EmployeeRetrieveUpdateDestroyAPIView.as_view(),
        name="employee-detail",
    ),

    path(
        "<int:employee_id>/status/",
        EmployeeStatusAPIView.as_view(),
        name="employee-status",
    ),

    # Departments
    path(
        "departments/",
        DepartmentListCreateAPIView.as_view(),
        name="department-list-create",
    ),

    path(
        "departments/<int:department_id>/",
        DepartmentRetrieveUpdateDestroyAPIView.as_view(),
        name="department-detail",
    ),
]