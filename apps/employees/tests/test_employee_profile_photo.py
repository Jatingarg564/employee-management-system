import io
from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from PIL import Image
from rest_framework import response, status
from apps.employees.models import Employee

from apps.employees.tests.base import EmployeeBaseAPITestCase


class EmployeeProfilePhotoAPITest(EmployeeBaseAPITestCase):

    def setUp(self):
        self.authenticate()

        self.temp_media = TemporaryDirectory()

        self.media_override = override_settings(
            MEDIA_ROOT=self.temp_media.name,
        )

        self.media_override.enable()

    def tearDown(self):
        self.media_override.disable()
        self.temp_media.cleanup()

    def create_image_file(
        self,
        image_format="JPEG",
        filename="profile.jpg",
        size=(200, 200),
    ):
        image = Image.new(
            "RGB",
            size,
            "white",
        )

        output = io.BytesIO()

        image.save(
            output,
            format=image_format,
        )

        output.seek(0)

        return SimpleUploadedFile(
            filename,
            output.read(),
            content_type=f"image/{image_format.lower()}",
        )

    def patch_employee(self, payload):
        return self.client.patch(
            self.employee_detail_url(),
            payload,
            format="multipart",
        )

    # ------------------------------------------------------------
    # Valid Image Uploads
    # ------------------------------------------------------------

    def test_upload_valid_jpeg(self):

        uploaded_file = self.create_image_file(
            image_format="JPEG",
            filename="my-photo.jpg",
        )

        response = self.patch_employee({
            "profile_photo": uploaded_file,
        })

        self.employee = Employee.objects.get(
            pk=self.employee.pk,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertTrue(
            self.employee.profile_photo,
        )

        self.assertNotEqual(
            self.employee.profile_photo.name,
            "my-photo.jpg",
        )

        self.assertTrue(
            self.employee.profile_photo.name.startswith(
                "employee_profiles/"
            )
        )

        self.assertTrue(
            Path(
                self.employee.profile_photo.path
            ).exists()
        )

    def test_upload_valid_png(self):

        uploaded_file = self.create_image_file(
            image_format="PNG",
            filename="my-photo.png",
        )

        response = self.patch_employee({
            "profile_photo": uploaded_file,
        })

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.employee = Employee.objects.get(
            pk=self.employee.pk,
        )

        self.assertTrue(
            self.employee.profile_photo.name.endswith(
                ".png"
            )
        )

    def test_upload_valid_webp(self):

        uploaded_file = self.create_image_file(
            image_format="WEBP",
            filename="my-photo.webp",
        )

        response = self.patch_employee({
            "profile_photo": uploaded_file,
        })

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.employee = Employee.objects.get(
            pk=self.employee.pk,
        )

        self.assertTrue(
            self.employee.profile_photo.name.endswith(
                ".webp"
            )
        )

    # ------------------------------------------------------------
    # Existing Photo Preservation
    # ------------------------------------------------------------

    def test_update_without_photo_preserves_existing_photo(self):

        uploaded_file = self.create_image_file()

        first_response = self.patch_employee({
            "profile_photo": uploaded_file,
        })

        self.assertEqual(
            first_response.status_code,
            status.HTTP_200_OK,
        )

        self.employee = Employee.objects.get(
            pk=self.employee.pk,
        )

        original_photo_name = (
            self.employee.profile_photo.name
        )

        original_photo_path = (
            self.employee.profile_photo.path
        )

        response = self.patch_employee({
            "first_name": "Updated Name",
        })

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.employee = Employee.objects.get(
            pk=self.employee.pk,
        )

        self.assertEqual(
            self.employee.profile_photo.name,
            original_photo_name,
        )

        self.assertTrue(
            Path(original_photo_path).exists()
        )

    # ------------------------------------------------------------
    # Invalid Uploads
    # ------------------------------------------------------------

    def test_non_image_file_is_rejected(self):

        uploaded_file = SimpleUploadedFile(
            "malicious.jpg",
            b"This is not actually an image.",
            content_type="image/jpeg",
        )

        response = self.patch_employee({
            "profile_photo": uploaded_file,
        })

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_image_larger_than_5mb_is_rejected(self):

        oversized_file = SimpleUploadedFile(
            "large.jpg",
            b"x" * (5 * 1024 * 1024 + 1),
            content_type="image/jpeg",
        )

        response = self.patch_employee({
            "profile_photo": oversized_file,
        })

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_image_dimensions_larger_than_4096_are_rejected(self):

        uploaded_file = self.create_image_file(
            image_format="JPEG",
            filename="huge.jpg",
            size=(4097, 100),
        )

        response = self.patch_employee({
            "profile_photo": uploaded_file,
        })

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # ------------------------------------------------------------
    # Photo Replacement
    # ------------------------------------------------------------

    def test_replacing_photo_deletes_old_file(self):

        first_file = self.create_image_file(
            filename="first.jpg",
        )

        first_response = self.patch_employee({
            "profile_photo": first_file,
        })

        self.assertEqual(
            first_response.status_code,
            status.HTTP_200_OK,
        )

        old_photo_name = first_response.data["profile_photo"]

        self.assertIsNotNone(
            old_photo_name,
        )

        self.employee.refresh_from_db()

        old_photo_path = Path(
            self.employee.profile_photo.path,
        )

        self.assertTrue(
            old_photo_path.exists()
        )

        second_file = self.create_image_file(
            filename="second.jpg",
        )

        with self.captureOnCommitCallbacks(
            execute=True,
        ):
            second_response = self.patch_employee({
                "profile_photo": second_file,
            })

        self.assertEqual(
            second_response.status_code,
            status.HTTP_200_OK,
        )

        new_photo_name = second_response.data["profile_photo"]

        self.employee.refresh_from_db()

        new_photo_path = Path(
            self.employee.profile_photo.path,
        )

        self.assertIsNotNone(
            new_photo_name,
        )

        self.assertNotEqual(
            old_photo_name,
            new_photo_name,
        )

        self.assertTrue(
            new_photo_path.exists()
        )

        self.assertFalse(
            old_photo_path.exists()
        )