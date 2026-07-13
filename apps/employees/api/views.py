from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.employees.api.serializers import (
    EmployeeCreateSerializer,
    EmployeeDetailSerializer,
)
from apps.employees.models import Employee
from apps.employees.services import EmployeeService


class EmployeeAPIView(APIView):
    """
    API view to handle employee-related operations.
    """

    def get(self, request, *args, **kwargs):
        """
        Retrieve all employees.
        """

        employees = Employee.objects.order_by("employee_code")

        detail_serializer = EmployeeDetailSerializer(
            employees,
            many=True,
        )

        return Response(
            detail_serializer.data,
            status=status.HTTP_200_OK,
        )

    def post(self, request, *args, **kwargs):
        """
        Create a new employee.
        """

        create_serializer = EmployeeCreateSerializer(
            data=request.data,
        )

        create_serializer.is_valid(
            raise_exception=True,
        )

        employee = EmployeeService.create_employee(
            create_serializer.validated_data,
        )

        detail_serializer = EmployeeDetailSerializer(
            employee,
        )

        return Response(
            detail_serializer.data,
            status=status.HTTP_201_CREATED,
        )