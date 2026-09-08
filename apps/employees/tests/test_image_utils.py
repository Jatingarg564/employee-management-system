import io

from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase
from rest_framework.exceptions import ValidationError

from apps.employees.image_utils import sanitize_profile_photo


class ProfilePhotoSanitizationTest(SimpleTestCase):

    def create_image(
        self,
        image_format="JPEG",
        size=(500, 500),
        filename="profile.jpg",
    ):
        image = Image.new(
            "RGB",
            size,
            "white",
        )

        image_data = io.BytesIO()

        image.save(
            image_data,
            format=image_format,
        )

        image_data.seek(0)

        return SimpleUploadedFile(
            name=filename,
            content=image_data.read(),
            content_type=f"image/{image_format.lower()}",
        )

    def test_valid_jpeg_is_accepted(self):

        uploaded_file = self.create_image(
            image_format="JPEG",
        )

        sanitized_file = sanitize_profile_photo(
            uploaded_file,
        )

        self.assertIsNotNone(
            sanitized_file,
        )

        with Image.open(sanitized_file) as image:
            self.assertEqual(
                image.format,
                "JPEG",
            )

    def test_valid_png_is_accepted(self):

        uploaded_file = self.create_image(
            image_format="PNG",
            filename="profile.png",
        )

        sanitized_file = sanitize_profile_photo(
            uploaded_file,
        )

        self.assertIsNotNone(
            sanitized_file,
        )

        with Image.open(sanitized_file) as image:
            self.assertEqual(
                image.format,
                "PNG",
            )

    def test_valid_webp_is_accepted(self):

        uploaded_file = self.create_image(
            image_format="WEBP",
            filename="profile.webp",
        )

        sanitized_file = sanitize_profile_photo(
            uploaded_file,
        )

        self.assertIsNotNone(
            sanitized_file,
        )

        with Image.open(sanitized_file) as image:
            self.assertEqual(
                image.format,
                "WEBP",
            )

    def test_non_image_file_is_rejected(self):

        uploaded_file = SimpleUploadedFile(
            name="profile.jpg",
            content=b"This is not an image.",
            content_type="image/jpeg",
        )

        with self.assertRaises(ValidationError):
            sanitize_profile_photo(
                uploaded_file,
            )

    def test_image_larger_than_5_mb_is_rejected(self):

        uploaded_file = SimpleUploadedFile(
            name="large.jpg",
            content=b"x" * (5 * 1024 * 1024 + 1),
            content_type="image/jpeg",
        )

        with self.assertRaises(ValidationError):
            sanitize_profile_photo(
                uploaded_file,
            )

    def test_image_larger_than_4096_pixels_is_rejected(self):

        uploaded_file = self.create_image(
            image_format="JPEG",
            size=(4097, 500),
        )

        with self.assertRaises(ValidationError):
            sanitize_profile_photo(
                uploaded_file,
            )

    def test_original_filename_is_not_used(self):

        uploaded_file = self.create_image(
            image_format="JPEG",
            filename="../../malicious.jpg",
        )

        sanitized_file = sanitize_profile_photo(
            uploaded_file,
        )

        self.assertNotEqual(
            sanitized_file.name,
            "../../malicious.jpg",
        )

        self.assertTrue(
            sanitized_file.name.startswith(
                "employee_"
            ),
        )

        self.assertTrue(
            sanitized_file.name.endswith(
                ".jpeg"
            ),
        )

    def test_sanitized_image_can_be_decoded(self):

        uploaded_file = self.create_image(
            image_format="JPEG",
        )

        sanitized_file = sanitize_profile_photo(
            uploaded_file,
        )

        with Image.open(sanitized_file) as image:
            image.load()

            self.assertEqual(
                image.size,
                (500, 500),
            )

    def test_none_is_allowed(self):

        sanitized_file = sanitize_profile_photo(
            None,
        )

        self.assertIsNone(
            sanitized_file,
        )

    def test_image_metadata_is_not_preserved(self):

        image = Image.new(
            "RGB",
            (500, 500),
            "white",
        )

        exif = image.getexif()

        exif[270] = "Sensitive employee metadata"
        exif[271] = "Example Camera"

        image_data = io.BytesIO()

        image.save(
            image_data,
            format="JPEG",
            exif=exif.tobytes(),
        )

        image_data.seek(0)

        uploaded_file = SimpleUploadedFile(
            name="profile.jpg",
            content=image_data.read(),
            content_type="image/jpeg",
        )

        sanitized_file = sanitize_profile_photo(
            uploaded_file,
        )

        with Image.open(sanitized_file) as sanitized_image:

            sanitized_exif = sanitized_image.getexif()

            self.assertNotIn(
                270,
                sanitized_exif,
            )

            self.assertNotIn(
                271,
                sanitized_exif,
            )