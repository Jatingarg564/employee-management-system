from django.urls import path
from apps.employees.api.views import EmployeeAPIView

urlpatterns = [
    path("employees/", EmployeeAPIView.as_view(), name="employee-list-create", ),
]