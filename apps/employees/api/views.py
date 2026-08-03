from drf_spectacular.utils import extend_schema, extend_schema_view
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
from rest_framework.permissions import IsAuthenticated


@extend_schema_view(
    get=extend_schema(
        tags=["Employees"],
        summary="List Employees",
        description="Retrieve all employees.",
        operation_id="list_employees",
        responses=EmployeeDetailSerializer(many=True),
    ),
    post=extend_schema(
        tags=["Employees"],
        summary="Create Employee",
        description="Create a new employee.",
        operation_id="create_employee",
        request=EmployeeCreateSerializer,
        responses={201: EmployeeDetailSerializer},
    ),
)
class EmployeeListCreateAPIView(APIView):
    """
    API view for listing employees and creating new employees.
    """
    permission_classes = [IsAuthenticated]

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


@extend_schema_view(
    get=extend_schema(
        tags=["Employees"],
        summary="Retrieve Employee",
        operation_id="retrieve_employee",
        responses=EmployeeDetailSerializer,
    ),
    put=extend_schema(
        tags=["Employees"],
        summary="Update Employee",
        operation_id="update_employee",
        request=EmployeeUpdateSerializer,
        responses=EmployeeDetailSerializer,
    ),
    patch=extend_schema(
        tags=["Employees"],
        summary="Partial Update Employee",
        operation_id="partial_update_employee",
        request=EmployeeUpdateSerializer,
        responses=EmployeeDetailSerializer,
    ),
    delete=extend_schema(
        tags=["Employees"],
        summary="Soft Delete Employee",
        operation_id="delete_employee",
        responses={204: None},
    ),
)
class EmployeeRetrieveUpdateDestroyAPIView(APIView):
    """
    API view for retrieving, updating and soft deleting an employee.
    """
    permission_classes = [IsAuthenticated]

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


@extend_schema_view(
    patch=extend_schema(
        tags=["Employees"],
        summary="Update Employee Status",
        description="Update the employment status of an employee.",
        operation_id="update_employee_status",
        request=EmployeeStatusUpdateSerializer,
        responses=EmployeeDetailSerializer,
    ),
)
class EmployeeStatusAPIView(APIView):
    """
    API view for updating employee status.
    """
    permission_classes = [IsAuthenticated]
    
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