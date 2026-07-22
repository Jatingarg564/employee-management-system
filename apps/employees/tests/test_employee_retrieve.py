from rest_framework import status

from apps.employees.tests.base import EmployeeBaseAPITestCase
from apps.employees.tests.factories import EmployeeFactory


class EmployeeRetrieveAPITest(EmployeeBaseAPITestCase):

    def setUp(self):
        self.authenticate()

    # ------------------------------------------------------------
    # LIST EMPLOYEES
    # ------------------------------------------------------------

    def test_list_employees(self):

        EmployeeFactory.create_employee()

        EmployeeFactory.create_employee()

        response = self.client.get(
            self.employee_list_url()
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data),
            EmployeeFactory.counter
        )

    # ------------------------------------------------------------
    # RETRIEVE SINGLE EMPLOYEE
    # ------------------------------------------------------------

    def test_retrieve_employee(self):

        response = self.client.get(
            self.employee_detail_url()
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data["id"],
            self.employee.id
        )

        self.assertEqual(
            response.data["employee_code"],
            self.employee.employee_code
        )

        self.assertEqual(
            response.data["email"],
            self.employee.email
        )

        self.assertEqual(
            response.data["first_name"],
            self.employee.first_name
        )

        self.assertEqual(
            response.data["last_name"],
            self.employee.last_name
        )

    # ------------------------------------------------------------
    # INVALID ID
    # ------------------------------------------------------------

    def test_retrieve_invalid_employee(self):

        response = self.client.get(
            "/api/employees/999999/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    # ------------------------------------------------------------
    # LIST SHOULD CONTAIN NEWLY CREATED EMPLOYEE
    # ------------------------------------------------------------

    def test_list_contains_new_employee(self):

        employee = EmployeeFactory.create_employee()

        response = self.client.get(
            self.employee_list_url()
        )

        ids = [
            emp["id"]
            for emp in response.data
        ]

        self.assertIn(
            employee.id,
            ids
        )

    # ------------------------------------------------------------
    # VERIFY EMPLOYEE FIELDS
    # ------------------------------------------------------------

    def test_employee_response_contains_expected_fields(self):

        response = self.client.get(
            self.employee_detail_url()
        )

        expected_fields = {

            "id",

            "employee_code",

            "first_name",

            "last_name",

            "email",

            "phone_number",

            "department",

            "designation",

            "reporting_to",

            "date_of_birth",

            "date_of_joining",

            "employment_type",

            "role",

            "status",

            "salary",

            "address",

            "profile_photo",

            "created_at",

            "updated_at",

        }

        self.assertTrue(
            expected_fields.issubset(
                response.data.keys()
            )
        )

    # ------------------------------------------------------------
    # EMPTY DATABASE
    # ------------------------------------------------------------

    def test_list_empty_database(self):

        self.employee.delete()
        self.manager.delete()

        response = self.client.get(
            self.employee_list_url()
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data),
            0
        )

    # ------------------------------------------------------------
    # AUTHENTICATION
    # ------------------------------------------------------------

    def test_list_requires_authentication(self):

        self.client.force_authenticate(None)

        response = self.client.get(
            self.employee_list_url()
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ]
        )

    def test_detail_requires_authentication(self):

        self.client.force_authenticate(None)

        response = self.client.get(
            self.employee_detail_url()
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ]
        )