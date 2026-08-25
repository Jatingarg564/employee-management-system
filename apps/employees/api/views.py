from django.db import transaction
from django.shortcuts import get_object_or_404

from drf_spectacular.utils import extend_schema, extend_schema_view

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.employees.api.serializers import (
    EmployeeCreateSerializer,
    EmployeeDetailSerializer,
    EmployeeStatusUpdateSerializer,
    EmployeeUpdateSerializer,
    DepartmentSerializer,
)

from apps.employees.models import (
    Employee,
    Department,
)

from apps.employees.services import (
    EmployeeService,
    DepartmentService,
)



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

@extend_schema_view(
    get=extend_schema(
        tags=["Departments"],
        summary="List Departments",
        description="Retrieve all departments.",
        operation_id="list_departments",
        responses=DepartmentSerializer(many=True),
    ),
    post=extend_schema(
        tags=["Departments"],
        summary="Create Department",
        description="Create a new department.",
        operation_id="create_department",
        request=DepartmentSerializer,
        responses={201: DepartmentSerializer},
    ),
)
class DepartmentListCreateAPIView(APIView):
    """
    API view for listing and creating departments.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Retrieve all departments.
        """

        departments = Department.objects.all()

        serializer = DepartmentSerializer(
            departments,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def post(self, request, *args, **kwargs):
        """
        Create a new department.
        """

        serializer = DepartmentSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        department = DepartmentService.create_department(
            serializer.validated_data,
        )

        response_serializer = DepartmentSerializer(
            department,
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )

@extend_schema_view(
    get=extend_schema(
        tags=["Departments"],
        summary="Retrieve Department",
        description="Retrieve a single department.",
        operation_id="retrieve_department",
        responses=DepartmentSerializer,
    ),
    put=extend_schema(
        tags=["Departments"],
        summary="Update Department",
        description="Fully update a department.",
        operation_id="update_department",
        request=DepartmentSerializer,
        responses=DepartmentSerializer,
    ),
    patch=extend_schema(
        tags=["Departments"],
        summary="Partial Update Department",
        description="Partially update a department.",
        operation_id="partial_update_department",
        request=DepartmentSerializer,
        responses=DepartmentSerializer,
    ),
    delete=extend_schema(
        tags=["Departments"],
        summary="Deactivate Department",
        description="Soft deactivate a department.",
        operation_id="deactivate_department",
        responses={204: None},
    ),
)


class DepartmentRetrieveUpdateDestroyAPIView(APIView):
    """
    API view for retrieving, updating and deactivating departments.
    """

    permission_classes = [IsAuthenticated]

    @staticmethod
    def get_department(department_id):
        """
        Retrieve a department instance.
        """

        return get_object_or_404(
            Department,
            pk=department_id,
        )

    def get(self, request, department_id, *args, **kwargs):
        """
        Retrieve a single department.
        """

        department = self.get_department(
            department_id,
        )

        serializer = DepartmentSerializer(
            department,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def put(self, request, department_id, *args, **kwargs):
        """
        Fully update a department.
        """

        department = self.get_department(
            department_id,
        )

        serializer = DepartmentSerializer(
            department,
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        department = DepartmentService.update_department(
            department,
            serializer.validated_data,
        )

        response_serializer = DepartmentSerializer(
            department,
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )

    def patch(self, request, department_id, *args, **kwargs):
        """
        Partially update a department.
        """

        department = self.get_department(
            department_id,
        )

        serializer = DepartmentSerializer(
            department,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        department = DepartmentService.update_department(
            department,
            serializer.validated_data,
        )

        response_serializer = DepartmentSerializer(
            department,
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )

    def delete(self, request, department_id, *args, **kwargs):
        """
        Soft deactivate a department.
        """

        department = self.get_department(
            department_id,
        )

        DepartmentService.deactivate_department(
            department,
        )

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )