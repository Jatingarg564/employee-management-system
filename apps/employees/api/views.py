from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.employees.api.serializers import (
    EmployeeCreateSerializer,
    EmployeeDetailSerializer,
    EmployeeStatusUpdateSerializer,
    EmployeeUpdateSerializer,
)
from apps.employees.models import Employee
from apps.employees.services import EmployeeService


class EmployeeListCreateAPIView(APIView):
    """
    API view for listing employees and creating new employees.
    """

    def get(self, request, *args, **kwargs):
        """
        Retrieve all employees.
        """

        employees = Employee.objects.order_by(
            "employee_code",
        )

        serializer = EmployeeDetailSerializer(
            employees,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def post(self, request, *args, **kwargs):
        """
        Create a new employee.
        """

        serializer = EmployeeCreateSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        employee = EmployeeService.create_employee(
            serializer.validated_data,
        )

        response_serializer = EmployeeDetailSerializer(
            employee,
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )


class EmployeeRetrieveUpdateDestroyAPIView(APIView):
    """
    API view for retrieving, updating and soft deleting an employee.
    """

    @staticmethod
    def get_employee(employee_id):
        """
        Retrieve an employee instance.
        """

        return get_object_or_404(
            Employee,
            pk=employee_id,
        )

    def get(self, request, employee_id, *args, **kwargs):
        """
        Retrieve a single employee.
        """

        employee = self.get_employee(
            employee_id,
        )

        serializer = EmployeeDetailSerializer(
            employee,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def put(self, request, employee_id, *args, **kwargs):
        """
        Fully update an employee.
        """

        employee = self.get_employee(
            employee_id,
        )

        serializer = EmployeeUpdateSerializer(
            employee,
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        employee = EmployeeService.update_employee(
            employee,
            serializer.validated_data,
        )

        response_serializer = EmployeeDetailSerializer(
            employee,
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )

    def patch(self, request, employee_id, *args, **kwargs):
        """
        Partially update an employee.
        """

        employee = self.get_employee(
            employee_id,
        )

        serializer = EmployeeUpdateSerializer(
            employee,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        employee = EmployeeService.update_employee(
            employee,
            serializer.validated_data,
        )

        response_serializer = EmployeeDetailSerializer(
            employee,
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )

    def delete(self, request, employee_id, *args, **kwargs):
        """
        Soft delete an employee.
        """

        employee = self.get_employee(
            employee_id,
        )

        EmployeeService.soft_delete_employee(
            employee,
        )

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )


class EmployeeStatusAPIView(APIView):
    """
    API view for updating employee status.
    """

    @staticmethod
    def get_employee(employee_id):
        """
        Retrieve an employee instance.
        """

        return get_object_or_404(
            Employee,
            pk=employee_id,
        )

    def patch(self, request, employee_id, *args, **kwargs):
        """
        Update employee status.
        """

        employee = self.get_employee(
            employee_id,
        )

        serializer = EmployeeStatusUpdateSerializer(
            employee,
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        employee = EmployeeService.update_employee_status(
            employee,
            serializer.validated_data,
        )

        response_serializer = EmployeeDetailSerializer(
            employee,
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )