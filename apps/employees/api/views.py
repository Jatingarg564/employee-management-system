from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.employees.api.serializers import EmployeeSerializer
from apps.employees.models import Employee
from apps.employees.services import EmployeeService

# Create your views here.

class EmployeeAPIView(APIView):
    """
    API view to handle employee-related operations.
    """

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to retrieve employee data.
        """
        employees = Employee.objects.all()
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to create a new employee.
        """

        serializer = EmployeeSerializer(data=request.data)

        if serializer.is_valid():

            employee = EmployeeService.create_employee(
                serializer.validated_data
            )

            response_serializer = EmployeeSerializer(employee)

            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )